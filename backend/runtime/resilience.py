from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Any, TypeVar

import tenacity
from circuitbreaker import CircuitBreakerError, circuit

log = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class TaskMetrics:
    attempts: int = 0
    latency_ms: float = 0.0
    success: bool = False
    error_type: str | None = None


class SwarmResilience:
    """Centralized resilience for swarm/agent tasks."""

    @staticmethod
    def retry_async(max_attempts: int = 3, wait_seconds: float = 1.0, exceptions: tuple = (Exception,)):
        """Decorator with exponential backoff + jitter."""
        return tenacity.retry(
            stop=tenacity.stop_after_attempt(max_attempts),
            wait=tenacity.wait_exponential_jitter(initial=wait_seconds, jitter=0.5),
            retry=tenacity.retry_if_exception_type(exceptions),
            before_sleep=lambda retry_state: log.warning(
                f"Retrying task after {retry_state.outcome.exception()} (attempt {retry_state.attempt_number})"
            ),
            reraise=True,
        )

    @staticmethod
    def circuit_breaker(fail_max: int = 5, reset_timeout: int = 30):
        """Circuit breaker decorator (open after N failures)."""
        return circuit(failure_threshold=fail_max, recovery_timeout=reset_timeout)

    @staticmethod
    async def run_with_resilience(
        coro: Awaitable[T],
        task_name: str,
        metrics: dict[str, Any] | None = None,
        timeout_seconds: float = 60.0,
    ) -> T:
        """Wrap any async task with timeout, retry, metrics, and logging."""
        start = time.time()
        task_metrics = TaskMetrics()

        try:
            async with asyncio.timeout(timeout_seconds):
                result = await coro
                task_metrics.success = True
                return result
        except TimeoutError:
            task_metrics.error_type = "timeout"
            log.error("[%s] Timeout after %ss", task_name, timeout_seconds)
            raise
        except CircuitBreakerError:
            task_metrics.error_type = "circuit_open"
            log.error("[%s] Circuit breaker open — failing fast", task_name)
            raise
        except Exception as exc:
            task_metrics.error_type = type(exc).__name__
            log.error("[%s] Failed: %s", task_name, exc)
            raise
        finally:
            task_metrics.latency_ms = (time.time() - start) * 1000
            # Note: tenacity attempt count isn't directly exposed on coro;
            # this works if run via tenacity.retry
            task_metrics.attempts = getattr(coro, "__attempt_number__", 1)
            if metrics is not None:
                metrics[task_name] = task_metrics.__dict__
            log.info("[%s] Completed: %s", task_name, task_metrics)
