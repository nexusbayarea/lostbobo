# backend/core/kernel/lineage/attribution.py
from typing import Any

from backend.core.kernel.lineage.graph import ProvenanceGraph


class AttributionEngine:
    """Summarizes who/what contributed to an execution."""

    async def summarize(self, execution_id: str) -> dict[str, Any]:
        graph = await ProvenanceGraph().build(execution_id)

        return {
            "execution_id": execution_id,
            "models": self._get_unique(graph, "foundation_model"),
            "agents": self._get_unique(graph, "agent"),
            "datasets": self._get_unique(graph, "dataset"),
            "hardware": self._get_unique(graph, "gpu_node"),
            "dag_nodes": self._get_unique(graph, "dag_node"),
            "total_events": len(graph.nodes),
            "summary": f"Execution {execution_id} used {len(graph.nodes)} components",
        }

    def _get_unique(self, graph: ProvenanceGraph, node_type: str) -> list[str]:
        return sorted(list({n["name"] for n in graph.nodes.values() if n.get("type") == node_type}))
