from collections import deque

from .graph import DAGGraph


class TopologicalScheduler:
    def resolve(self, graph: DAGGraph) -> list[str]:
        """Deterministic topological order."""
        indegree = {nid: 0 for nid in graph.nodes}
        for edge in graph.edges:
            indegree[edge.target] += 1

        queue = deque([nid for nid, d in indegree.items() if d == 0])
        order = []

        while queue:
            current = queue.popleft()
            order.append(current)
            for neighbor in graph.get_downstream(current):
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(graph.nodes):
            raise RuntimeError("Cycle detected in DAG")
        return order
