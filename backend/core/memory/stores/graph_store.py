from __future__ import annotations

from typing import Any


class GraphStore:
    def __init__(self):
        self._edges: list[dict[str, Any]] = []
        self._nodes: dict[str, dict[str, Any]] = {}

    def add_edge(self, source: str, target: str, edge_type: str = "related", metadata: dict | None = None):
        self._edges.append(
            {
                "source": source,
                "target": target,
                "edge_type": edge_type,
                "metadata": metadata or {},
            }
        )

    def add_node(self, node_id: str, properties: dict[str, Any] | None = None) -> None:
        self._nodes[node_id] = properties or {}

    @property
    def edges(self) -> list[dict[str, Any]]:
        return self._edges

    def get_neighbors(self, node_id: str) -> list[str]:
        neighbors = set()
        for e in self._edges:
            if e["source"] == node_id:
                neighbors.add(e["target"])
            if e["target"] == node_id:
                neighbors.add(e["source"])
        return list(neighbors)

    async def handle_query(self, payload: dict[str, Any]) -> dict[str, Any]:
        if "traverse" in payload:
            start = payload["traverse"].get("start_node")
            if not start:
                raise ValueError("traverse requires start_node")
            depth = payload["traverse"].get("depth", 2)
            visited: set[str] = set()
            results: list[dict[str, Any]] = []
            queue = [(start, 0)]
            while queue:
                nid, d = queue.pop(0)
                if nid in visited or d > depth:
                    continue
                visited.add(nid)
                results.append({"node": nid, "depth": d})
                for neighbor in self.get_neighbors(nid):
                    queue.append((neighbor, d + 1))
            return {"paths": results}

        if "shortest_path" in payload:
            sp = payload["shortest_path"]
            from_node, to_node = sp.get("from"), sp.get("to")
            if not from_node or not to_node:
                raise ValueError("shortest_path requires from and to")
            visited_paths: dict[str, list[str]] = {from_node: [from_node]}
            queue = [from_node]
            while queue:
                current = queue.pop(0)
                if current == to_node:
                    return {"path": visited_paths[current]}
                for neighbor in self.get_neighbors(current):
                    if neighbor not in visited_paths:
                        visited_paths[neighbor] = visited_paths[current] + [neighbor]
                        queue.append(neighbor)
            return {"path": []}

        if "query_nodes" in payload:
            qn = payload["query_nodes"]
            key, value = qn.get("key"), qn.get("value")
            if not key or value is None:
                raise ValueError("query_nodes requires key and value")
            matches = [
                {"node_id": nid, "properties": props} for nid, props in self._nodes.items() if props.get(key) == value
            ]
            return {"nodes": matches}

        raise ValueError(f"Invalid graph query payload: {list(payload.keys())}")
