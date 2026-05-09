from typing import Any

from .graph import DAGGraph
from .incremental import DirtyTracker
from .scheduler import TopologicalScheduler


class DAGRuntime:
    def __init__(self):
        self.scheduler = TopologicalScheduler()
        self.dirty = DirtyTracker()

    async def execute(self, graph: DAGGraph, context: dict[str, Any]) -> dict[str, Any]:
        order = self.scheduler.resolve(graph)
        results: dict[str, Any] = {}

        for node_id in order:
            if not self.dirty.is_dirty(node_id):
                continue

            node = graph.nodes[node_id]
            result = await node.execute(context | {"results": results})
            results[node_id] = result
            self.dirty.clear(node_id)

        return results
