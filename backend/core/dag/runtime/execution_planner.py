from collections import defaultdict, deque


class ExecutionPlanner:
    def execution_plan(self, dag) -> list[list[str]]:
        """
        Returns a list of execution levels.
        Each level is a list of node_ids that can run in parallel.
        """
        # Build adjacency and in-degree
        graph = defaultdict(list)
        indeg = defaultdict(int)

        # Assume dag.nodes has node_id attribute
        # Assume dag.edges has source, target attributes
        for edge in dag.edges:
            graph[edge.source_node].append(edge.target_node)
            indeg[edge.target_node] += 1

        # Initialize queue with nodes having in-degree 0
        queue = deque([n.id for n in dag.nodes if indeg[n.id] == 0])
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
