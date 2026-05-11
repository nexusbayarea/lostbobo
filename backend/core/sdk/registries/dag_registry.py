from __future__ import annotations


class DAGRegistry:
    def __init__(self):
        self._nodes = {}

    def register_node(self, node_type: str, executor, plugin_name: str):
        self._nodes[node_type] = {
            "executor": executor,
            "plugin": plugin_name,
        }

    async def execute(self, node_type: str, payload: dict):
        if node_type not in self._nodes:
            raise ValueError(f"DAG node '{node_type}' not found")
        node = self._nodes[node_type]
        return await node["executor"](payload)
