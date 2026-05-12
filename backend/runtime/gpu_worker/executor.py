from __future__ import annotations

import asyncio
import time
from typing import Any

from backend.core.determinism.seeds.deterministic_seed_manager import DeterministicSeedManager
from backend.core.hardware.isolation import GPUIsolationManager
from backend.runtime.gpu_worker.telemetry import TelemetryAgent

gpu_manager = GPUIsolationManager()
seed_manager = DeterministicSeedManager()


async def execute_job(job: dict[str, Any], agent: TelemetryAgent) -> dict[str, Any]:
    execution_id = job["execution_id"]
    capability = job["capability"]
    job.get("inputs", {})

    seed = seed_manager.derive_seed(execution_id)
    seed_manager.apply_seed(seed)

    await agent.emit(execution_id, "job.started", {"capability": capability})

    start = time.time()
    try:
        await asyncio.sleep(2)

        result = {
            "output": f"simulated {capability}",
            "execution_id": execution_id,
            "deterministic_hash": "abc123",
        }

        duration = time.time() - start
        await agent.emit(execution_id, "job.completed", {"duration_ms": duration * 1000})

        return result
    except Exception as e:
        await agent.emit(execution_id, "job.failed", {"error": str(e)})
        raise
