from __future__ import annotations

from backend.core.sdk.base_plugin import (
    BasePlugin,
)
from backend.plugins.physics.dag_nodes.beam_solver import (
    solve_beam,
)
from backend.plugins.physics.manifest import (
    manifest,
)


class Plugin(BasePlugin):
    manifest = manifest

    async def register(self, kernel) -> None:
        kernel.capabilities.register(
            "physics.solve",
            self.solve,
        )

        kernel.dag.register_node(
            "beam.solve",
            solve_beam,
        )

    async def solve(
        self,
        payload: dict,
    ):
        return {
            "plugin": "physics",
            "status": "executed",
            "payload": payload,
        }
