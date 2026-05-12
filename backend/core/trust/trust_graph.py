from __future__ import annotations

from typing import Any


class TrustGraphAnalyzer:
    def __init__(self):
        self._edges: list[dict[str, Any]] = []

    def record_edge(self, source: str, target: str, metadata: dict | None = None):
        self._edges.append(
            {
                "source": source,
                "target": target,
                "metadata": metadata or {},
            }
        )

    def edge_exists(self, source: str, target: str) -> bool:
        return any(e["source"] == source and e["target"] == target for e in self._edges)

    def get_edges_for(self, plugin_id: str) -> list[dict[str, Any]]:
        return [e for e in self._edges if e["source"] == plugin_id or e["target"] == plugin_id]
