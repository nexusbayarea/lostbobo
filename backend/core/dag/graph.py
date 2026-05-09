from collections import defaultdict

from .edge import DAGEdge
from .node import DAGNode


class DAGGraph:
    def __init__(self):
        self.nodes: dict[str, DAGNode] = {}
        self.edges: list[DAGEdge] = []
        self.adjacency: dict[str, list[str]] = defaultdict(list)

    def add_node(self, node: DAGNode):
        self.nodes[node.id] = node

    def add_edge(self, edge: DAGEdge):
        self.edges.append(edge)
        self.adjacency[edge.source].append(edge.target)

    def get_downstream(self, node_id: str) -> list[str]:
        return self.adjacency[node_id]
