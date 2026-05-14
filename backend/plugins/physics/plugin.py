from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.core.sdk.abi.plugin_manifest import PluginManifest
from backend.core.sdk.base_plugin import BasePlugin
from backend.plugins.physics.schemas.molecule import MoleculeInput
from backend.plugins.physics.solvers.schrodinger import _get_backend, solve_schrodinger


class PhysicsPlugin(BasePlugin):
    def __init__(self):
        manifest_path = Path(__file__).parent / "manifest.json"
        with open(manifest_path) as f:
            data = json.load(f)
        self.manifest = PluginManifest(**data)

    async def register(self, kernel: Any) -> None:
        kernel.capability_registry.register(
            "physics.solve",
            self.capability_solve,
            plugin_name="physics",
            version="1.0.0",
            deterministic=True,
            timeout_seconds=3600,
        )
        kernel.capability_registry.register(
            "physics.simulate",
            self.capability_simulate,
            plugin_name="physics",
            version="1.0.0",
            deterministic=True,
            timeout_seconds=7200,
        )
        kernel.capability_registry.register(
            "physics.backend.status",
            self.capability_backend_status,
            plugin_name="physics",
            version="1.0.0",
            deterministic=False,
            timeout_seconds=30,
        )

        from backend.plugins.physics.dag_nodes.beam_solve import beam_solve

        kernel.dag_registry.register_node(
            "beam.solve",
            beam_solve,
            plugin_name="physics",
            deterministic=True,
            idempotent=True,
            max_retries=0,
            timeout_seconds=3600,
        )

        from backend.plugins.physics.dag_nodes.schrodinger_solve import schrodinger_solve

        kernel.dag_registry.register_node(
            "schrodinger.solve",
            schrodinger_solve,
            plugin_name="physics",
            deterministic=True,
            idempotent=True,
            max_retries=1,
            timeout_seconds=7200,
        )

    async def capability_solve(self, payload: dict[str, Any]) -> dict[str, Any]:
        molecule = MoleculeInput(**payload["molecule"])
        backend = payload.get("backend", "pyscf")
        result = await solve_schrodinger(molecule, backend=backend)
        return result.model_dump()

    async def capability_simulate(self, payload: dict[str, Any]) -> dict[str, Any]:
        molecule = MoleculeInput(**payload["molecule"])
        backend = payload.get("backend", "pyscf")
        result = await solve_schrodinger(molecule, backend=backend)
        return {
            **result.model_dump(),
            "simulation_type": payload.get("type", "single_point"),
        }

    async def capability_backend_status(self, payload: dict[str, Any]) -> dict[str, Any]:
        statuses: dict[str, Any] = {}
        for name in ["pyscf", "psi4", "orca"]:
            try:
                backend = _get_backend(name)
                available = await backend.is_available()
                statuses[name] = {
                    "available": available,
                    "capabilities": await backend.get_capabilities() if available else None,
                }
            except Exception as e:
                statuses[name] = {"available": False, "error": str(e)}
        return {"backends": statuses}


plugin = PhysicsPlugin()
