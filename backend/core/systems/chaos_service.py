from __future__ import annotations

from typing import Any

from backend.core.runtime.state_registry.service import StateRegistryService
from backend.core.services.observability_service import observability
from backend.core.tracing import trace_context


class ChaosService:
    """Singleton — orchestrates all chaos experiments."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def chaos(cls) -> ChaosService:
        return cls()

    async def inject(self, experiment: str, intensity: float = 0.3, duration_s: int = 60) -> dict[str, Any]:
        """Kernel command entrypoint for chaos injection."""
        with trace_context("chaos.inject", {"experiment": experiment}) as span:
            obs = observability()
            obs.increment("chaos_injections_total", tags={"experiment": experiment})

            # Record pre-chaos state for rollback
            pre_state = await StateRegistryService.registry().get_current()

            result = await self._run_experiment(experiment, intensity, duration_s)

            # Post-chaos validation + rollback if needed
            await self._validate_and_rollback(pre_state, result)

            span.set_attribute("experiment", experiment)
            span.set_attribute("intensity", intensity)
            return result

    async def _run_experiment(self, experiment: str, intensity: float, duration_s: int) -> dict[str, Any]:
        """Stub for actual experiment runners (LitmusChaos/Chaos Monkey)."""
        if experiment == "event_drop":
            await self._chaos_monkey_event_drop(intensity)
        elif experiment == "state_corruption":
            await self._chaos_monkey_state_corruption(intensity)
        elif experiment == "temporal_skew":
            await self._chaos_monkey_temporal_skew(intensity, duration_s)
        return {"status": "injected", "experiment": experiment}

    async def _chaos_monkey_event_drop(self, intensity: float) -> None:
        """Randomly drop events."""
        pass

    async def _chaos_monkey_state_corruption(self, intensity: float) -> None:
        """Simulate state corruption."""
        pass

    async def _chaos_monkey_temporal_skew(self, intensity: float, duration: int) -> None:
        """Simulate temporal skew."""
        pass

    async def _validate_and_rollback(self, pre_state: Any, result: dict[str, Any]) -> None:
        """Validate state post-chaos."""
        pass
