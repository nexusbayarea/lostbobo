"""
SimHPC Kernel (v3.0.0)
The heart of the runtime, managing capabilities and execution state.
"""

from typing import Any

from backend.runtime.contract import CONTRACT
from backend.runtime.execution_log import ExecutionLog


class Kernel:
    def __init__(self):
        self.log = ExecutionLog()
        self.active_capabilities = {"physics", "dag"}

    def execute(self, node: dict) -> dict:
        """Central execution point for all nodes."""
        print(f"[KERNEL] Executing {node.get('type')} -> {node.get('id', 'unknown')}")

        if node.get("type") == "mfem.solve":
            from backend.runtime.physics_nodes import run_mfem_solve

            return run_mfem_solve(node)

        return {"status": "ok", "node": node.get("id")}

    def boot(self, manifest: dict[str, Any] | None = None):
        print("[KERNEL] Initializing boot sequence...")

        if manifest is None:
            from backend.runtime.manifest import load_manifest

            manifest = load_manifest()

        if not CONTRACT.validate_manifest(manifest):
            raise RuntimeError("Kernel boot aborted: Manifest violates system contract.")

        if manifest.get("capabilities", {}).get("state_enabled"):
            self._init_state_subsystem()

        print("[KERNEL] Physics + DAG Engine Online")
        return {"status": "booted", "capabilities": list(self.active_capabilities)}

    def _init_state_subsystem(self):
        print("[KERNEL] State subsystem initialized.")


KERNEL = Kernel()

if __name__ == "__main__":
    KERNEL.boot({"capabilities": {"state_enabled": True}})
