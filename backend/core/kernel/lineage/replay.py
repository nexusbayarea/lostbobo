# backend/core/kernel/lineage/replay.py
from typing import Any

from backend.core.kernel.lineage.graph import ProvenanceGraph


class ExecutionReplay:
    """Deterministic replay from provenance graph."""

    async def replay(self, execution_id: str) -> dict[str, Any]:
        """Reconstruct execution state from lineage."""
        graph = await ProvenanceGraph().build(execution_id)

        return {
            "execution_id": execution_id,
            "graph": graph.to_dict(),
            "models_used": self._extract_models(graph),
            "agents_used": self._extract_agents(graph),
            "hardware_used": self._extract_hardware(graph),
            "replay_possible": True,
        }

    def _extract_models(self, graph: ProvenanceGraph) -> list[str]:
        return [n["name"] for n in graph.nodes.values() if n.get("type") == "foundation_model"]

    def _extract_agents(self, graph: ProvenanceGraph) -> list[str]:
        return [n["name"] for n in graph.nodes.values() if n.get("type") == "agent"]

    def _extract_hardware(self, graph: ProvenanceGraph) -> list[str]:
        return [n["name"] for n in graph.nodes.values() if n.get("type") == "gpu_node"]
