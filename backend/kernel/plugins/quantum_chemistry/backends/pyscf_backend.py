from typing import Any

import structlog

log = structlog.get_logger(__name__)


class PySCFBackend:
    """Mock backend for environments where PySCF cannot be built (e.g. windows/missing compilers)."""

    def __init__(self):
        self.results = {}

    async def initialize(self, context: dict[str, Any]) -> bool:
        log.info("Quantum chemistry initialized (Mock Mode)")
        self.results = {"energy": -76.0, "mock": True, "converged": True}
        return True

    async def step(self, dt: float, exchanged: dict[str, Any]) -> dict[str, Any]:
        temp = exchanged.get("temperature", 298.15)
        self.results = {
            "energy": -76.5 + temp * 0.001,
            "forces": [[0.01, 0.02, 0.03]],
            "dipole": [0.5, 0.3, 0.1],
            "homo_lumo_gap": 2.8,
            "backend": "mock",
            "converged": True,
        }
        log.info("Quantum calculation completed (Mock Mode)")
        return self.results

    async def export_state(self) -> dict[str, Any]:
        return self.results

    async def validate(self) -> dict[str, Any]:
        return {"valid": True, "energy": self.results.get("energy"), "issues": []}

    async def checkpoint(self) -> str:
        return "mock_checkpoint"
