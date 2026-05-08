"""
ChaosService — Kernel-managed chaos orchestration.
"""

from __future__ import annotations

from typing import Any

import structlog

from backend.core.kernel.kernel import Kernel
from backend.core.supabase_job_store import SupabaseJobStore
from backend.runtime.chaos_monkey import chaos_monkey

log = structlog.get_logger(__name__)


class ChaosService:
    """Kernel-centered Chaos Engineering Service."""

    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.supabase = SupabaseJobStore()
        self.chaos_monkey = chaos_monkey

    async def run_gameday(self, payload: dict[str, Any]) -> dict[str, Any]:
        job_id = await self.supabase.create_job("chaos_gameday", payload)

        experiment = payload.get("experiment", "cross-rag-physics-parallel")
        iterations = payload.get("iterations", 1)

        self.chaos_monkey.config.enabled = True
        self.chaos_monkey.config.probability = payload.get("chaos_probability", 0.15)

        results = []
        for i in range(iterations):
            # Execute via existing hybrid chaos infrastructure
            experiment_result = await self.kernel.services["orchestrator"].run_chaos_experiment(experiment)

            # Record everything in Supabase
            await self.supabase.record_event(
                "chaos_experiment_completed",
                {
                    "job_id": job_id,
                    "iteration": i,
                    "experiment": experiment,
                    "result": experiment_result,
                    "tenant_id": payload.get("tenant_id"),
                },
            )
            results.append(experiment_result)

        final_report = {
            "job_id": job_id,
            "experiments_run": len(results),
            "failures_injected": self.chaos_monkey.failures_injected,
            "success_rate": (sum(1 for r in results if r.get("success")) / len(results) if results else 0),
        }

        await self.supabase.update_job(job_id, status="completed", result=final_report)
        return final_report
