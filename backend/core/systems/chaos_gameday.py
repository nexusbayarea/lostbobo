from __future__ import annotations

from typing import Any

from backend.core.runtime.event_fabric.log import EventLogService
from backend.core.runtime.event_fabric.schema import SimHPCEvent
from backend.core.runtime.state_registry.service import StateRegistryService
from backend.core.systems.chaos_service import ChaosService


class GameDayOrchestrator:
    """Scheduled, fully automated chaos game days with rollback + post-mortem."""

    async def run_scenario(self, scenario_name: str, duration_s: int = 300):
        pre_snapshot = await StateRegistryService.registry().get_current()

        # Run chaos experiment
        await ChaosService.chaos().inject(scenario_name, intensity=0.5, duration_s=duration_s)

        # Automatic rollback to pre-chaos state
        await StateRegistryService.registry().reconstruct(pre_snapshot.timestamp)

        # Post-mortem report
        report = await self._generate_post_mortem(pre_snapshot)
        await EventLogService.event_log().publish(
            SimHPCEvent(
                event_type="chaos.gameday.post_mortem",
                source_plugin="kernel",
                priority="high",
                payload=report,
            )
        )

    async def _generate_post_mortem(self, pre_snapshot: Any) -> dict:
        """Generates post-mortem report."""
        return {"report": "mock_post_mortem"}
