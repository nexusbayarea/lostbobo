"""Planner Agent — uses Kernel for all execution."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from backend.core.kernel.kernel import Kernel

from backend.core.models.hypothesis import Hypothesis
from backend.core.simulation.runner import SimulationRunner


class PlannerAgent:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.runner = SimulationRunner()

    async def run(self, input_data: dict[str, Any]) -> Hypothesis:
        query = input_data.get("query", "")

        depth_context = await self.kernel.execute({"type": "DEPTH_QUERY", "payload": {"query": query, "top_k": 6}})

        hyp = Hypothesis()
        hyp.sim_params = input_data
        result = await self.runner.run(hyp)

        plan_result = {"plan": str(result), "depth_context_used": len(depth_context)}

        await self.kernel.execute(
            {
                "type": "MEMORY_RECORD",
                "payload": {
                    "type": "decision",
                    "content": {"plan": plan_result, "goal": input_data.get("goal")},
                },
            }
        )

        await self.kernel.execute(
            {"type": "DEPTH_STORE", "payload": {"layer": "planner", "state": plan_result, "metadata": {"query": query}}}
        )

        return plan_result
