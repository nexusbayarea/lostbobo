from __future__ import annotations

from typing import Any

from backend.runtime.scientific.adapters.base import SolverConfig
from backend.runtime.scientific.adapters.glvis_adapter import GLVisAdapter
from backend.runtime.scientific.adapters.mfem_adapter import MFEMAdapter
from backend.runtime.scientific.adapters.sundials_adapter import SUNDIALSAdapter


class ScientificSimulationExecutor:
    def __init__(self):
        self.adapters = {
            "mfem": MFEMAdapter(),
            "sundials": SUNDIALSAdapter(),
            "glvis": GLVisAdapter(),
        }

    async def execute(self, job: dict[str, Any]) -> dict[str, Any]:
        cap = job.get("capability")
        if not cap or cap not in ("physics.solve", "simulation.run"):
            raise ValueError(f"Unsupported capability for scientific executor: {cap}")

        solver_type = job.get("solver_type", "mfem")
        adapter = self.adapters.get(solver_type)
        if not adapter:
            raise ValueError(f"Unknown solver type: {solver_type}")

        config_data = job.get("config", {})
        config = SolverConfig(
            solver_type=solver_type,
            parameters=config_data.get("parameters", {}),
            mesh_data=config_data.get("mesh_data"),
        )
        inputs = job.get("inputs", {})

        if not await adapter.validate(config):
            raise ValueError("Solver configuration invalid")

        result = await adapter.run(config, inputs)
        return result
