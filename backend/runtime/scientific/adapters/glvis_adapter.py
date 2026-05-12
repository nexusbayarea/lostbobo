from __future__ import annotations

from typing import Any

from backend.runtime.scientific.adapters.base import ScientificAdapter, SolverConfig


class GLVisAdapter(ScientificAdapter):
    async def validate(self, config: SolverConfig) -> bool:
        return True

    async def run(self, config: SolverConfig, inputs: dict[str, Any]) -> dict[str, Any]:
        try:
            import mfem

            sock = mfem.socketstream("localhost", 19916)
            sock.precision(8)
            mesh = inputs.get("mesh")
            solution = inputs.get("solution")
            if mesh and solution:
                sock.send_solution(mesh, solution)
                return {"status": "sent"}
        except Exception:
            pass
        return {"status": "no_glvis_server"}
