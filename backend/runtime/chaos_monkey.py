from __future__ import annotations

import asyncio
import functools
import random
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import TypeVar

import structlog

log = structlog.get_logger(__name__)

T = TypeVar("T")


class ChaosAction(Enum):
    LATENCY = "latency"
    EXCEPTION = "exception"
    TIMEOUT = "timeout"
    CIRCUIT_TRIGGER = "circuit_trigger"  # force failures to open breaker
    PARTIAL_SUCCESS = "partial_success"


@dataclass
class ChaosConfig:
    enabled: bool = False
    probability: float = 0.15  # 15% chance per task
    max_latency_ms: int = 8000
    exceptions: list[type[Exception]] = field(
        default_factory=lambda: [RuntimeError, ConnectionError, asyncio.TimeoutError]
    )


class SimHPCChaosMonkey:
    """Chaos Monkey for SimHPC swarm / agent tasks."""

    def __init__(self, config: ChaosConfig | None = None):
        self.config = config or ChaosConfig()
        self.experiments_run = 0
        self.failures_injected = 0

    def should_chaos(self) -> bool:
        """Decide whether to inject chaos for this invocation."""
        return self.config.enabled and random.random() < self.config.probability

    async def inject_chaos(self, task_name: str, coro: Awaitable[T]) -> T:
        """Wrap a coroutine and possibly inject chaos."""
        if not self.should_chaos():
            return await coro

        self.experiments_run += 1
        action = random.choice(list(ChaosAction))

        log.warning("🐵 CHAOS MONKEY activated on [%s] → %s", task_name, action.value)

        start = time.time()

        try:
            if action == ChaosAction.LATENCY:
                await asyncio.sleep(random.uniform(1.0, self.config.max_latency_ms / 1000))
                return await coro

            if action == ChaosAction.TIMEOUT:
                # Force timeout by delaying beyond typical limits
                await asyncio.sleep(65)  # longer than most task timeouts
                return await coro

            if action == ChaosAction.EXCEPTION:
                exc_type = random.choice(self.config.exceptions)
                self.failures_injected += 1
                raise exc_type(f"Chaos Monkey injected {exc_type.__name__} in {task_name}")

            if action == ChaosAction.CIRCUIT_TRIGGER:
                # Trigger multiple failures to open circuit breaker
                for _ in range(6):  # exceed typical fail_max=5
                    try:
                        raise RuntimeError("Circuit breaker stress test")
                    except Exception:
                        pass
                self.failures_injected += 1
                raise RuntimeError("Circuit breaker forced open")

            if action == ChaosAction.PARTIAL_SUCCESS:
                # Return early with degraded result
                result = await asyncio.wait_for(coro, timeout=3.0)
                log.info("🐵 Partial success chaos on %s", task_name)
                return result  # or modify result if needed

        except Exception as e:
            log.error("🐵 Chaos injected failure in %s: %s", task_name, e)
            raise
        finally:
            duration = (time.time() - start) * 1000
            log.info("🐵 Chaos experiment completed on %s in %.1fms", task_name, duration)

    def wrap(self, func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        """Decorator to easily wrap agent/swarm methods."""

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            task_name = kwargs.get("task_name") or func.__name__
            coro = func(*args, **kwargs)
            return await self.inject_chaos(task_name, coro)

        return wrapper


# Global singleton (enable via env var or config)
chaos_monkey = SimHPCChaosMonkey(
    ChaosConfig(enabled=True, probability=0.12, max_latency_ms=5000)  # Toggle in dev/staging
)
