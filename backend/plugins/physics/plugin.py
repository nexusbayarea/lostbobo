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
from backend.plugins.physics.orchestrators.beam_orchestrator import (
    BeamOrchestrator,
)


class Plugin(BasePlugin):
    manifest = manifest

    async def register(self, kernel) -> None:
        # Register the beam solve capability (DAG node)
        kernel.dag.register_node(
            "beam.solve",
            solve_beam,
        )

        # Register the physics solve capability (high-level interface)
        kernel.capabilities.register(
            "physics.solve",
            self.solve,
        )

        # Register the physics beam orchestration capability
        kernel.capabilities.register(
            "physics.beam.orchestrate",
            self.orchestrate_beam,
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

    async def orchestrate_beam(
        self,
        payload: dict,
    ):
        """
        Orchestrate a beam physics computation using the full BeamOrchestrator.
        Expected payload: {
            "query": str,
            "tenant_id": str (optional),
            "request_id": str (optional)
        }
        """
        # Extract parameters from payload
        query = payload.get("query", "")
        tenant_id = payload.get("tenant_id", "public")
        request_id = payload.get("request_id")

        # Initialize the orchestrator with default empty agents list
        # In a real implementation, agents would be provided via dependency injection
        orchestrator = BeamOrchestrator(
            agents=[],  # Would be injected in real implementation
            rag=None,  # Would be injected in real implementation
            config={},  # Would be configured in real implementation
        )

        # Run the orchestration
        result = await orchestrator.run(query=query, tenant_id=tenant_id, request_id=request_id)

        return {
            "plugin": "physics",
            "capability": "physics.beam.orchestrate",
            "status": "completed",
            "result": {
                "hypothesis": {
                    "id": result.id,
                    "query": result.query,
                    "context": result.context,
                    "trust_score": result.trust_score,
                    "stage": result.stage,
                },
                "validation_passed": hasattr(result, "validation_passed") and result.validation_passed,
            },
            "payload": payload,
        }
