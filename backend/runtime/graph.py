from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class Node:
    id: str
    fn: Callable[..., Any]
    deps: list[str] = None
    metadata: dict = None

    def __post_init__(self):
        if self.deps is None:
            self.deps = []
        if self.metadata is None:
            self.metadata = {}


class ExecutionGraph:
    def __init__(self):
        self.nodes: dict[str, Node] = {}

    def register(self, node: Node):
        if node.id in self.nodes:
            raise ValueError(f"Duplicate node: {node.id}")
        self.nodes[node.id] = node

    def get(self, node_id: str) -> Node:
        return self.nodes[node_id]

    def topological_sort(self) -> list[str]:
        """Return nodes in topological execution order."""
        visited = set()
        visiting = set()
        order = []

        def visit(nid: str):
            if nid in visiting:
                raise RuntimeError(f"Cyclic dependency detected at node: {nid}")
            if nid in visited:
                return

            visiting.add(nid)
            node = self.nodes[nid]
            for dep in node.deps:
                visit(dep)

            visiting.remove(nid)
            visited.add(nid)
            order.append(nid)

        for nid in self.nodes:
            visit(nid)

        return order


# Global singleton
GRAPH = ExecutionGraph()
