from __future__ import annotations

from collections import defaultdict, deque

from backend.core.dag.ir.dag_ir import DAGIR


class ExecutionPlanner:
    def execution_plan(self, dag: DAGIR) -> list[list[str]]:
        graph = defaultdict(list)
        indeg = defaultdict(int)
        for edge in dag.edges:
            graph[edge.source].append(edge.target)
            indeg[edge.target] += 1

        queue = deque([n.node_id for n in dag.nodes if indeg[n.node_id] == 0])
        levels = []

        while queue:
            level = list(queue)
            levels.append(level)
            next_queue = deque()
            for node_id in level:
                for neighbor in graph[node_id]:
                    indeg[neighbor] -= 1
                    if indeg[neighbor] == 0:
                        next_queue.append(neighbor)
            queue = next_queue
        return levels
