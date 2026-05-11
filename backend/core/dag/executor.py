"""
Deterministic DAG executor.
Relies on kernel registries – no direct plugin imports.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from backend.core.dag.models import DAGGraph
from backend.core.sdk.registries.dag_registry import DAGRegistry


class DAGExecutionError(Exception):
    """Raised when DAG execution fails."""

    pass


class DAGExecutor:
    def __init__(self, dag_registry: DAGRegistry):
        self.registry = dag_registry

    async def execute(self, graph: DAGGraph, global_inputs: dict[str, Any]) -> dict[str, Any]:
        # 1. Resolve entry node
        if graph.entry_node is None:
            graph.entry_node = self._find_entry_node(graph)

        # 2. Build adjacency and in-degree map
        in_degree: dict[str, int] = {n.id: 0 for n in graph.nodes}
        edge_map: dict[str, list[tuple]] = defaultdict(list)
        for edge in graph.edges:
            edge_map[edge.source_node].append((edge.source_port, edge.target_node, edge.target_port, edge.condition))
            in_degree[edge.target_node] += 1

        # 3. Topological sort execution
        queue: deque = deque()
        for node in graph.nodes:
            if in_degree[node.id] == 0:
                queue.append(node.id)

        if not queue:
            raise DAGExecutionError("DAG contains a cycle or has no entry point")

        results: dict[str, dict[str, Any]] = {}  # node_id -> output dict
        target_inputs: dict[str, dict[str, Any]] = defaultdict(dict)

        # Merge global inputs into entry node inputs if necessary
        for node in graph.nodes:
            if node.id == graph.entry_node:
                target_inputs[node.id].update(global_inputs)

        while queue:
            node_id = queue.popleft()
            node = next(n for n in graph.nodes if n.id == node_id)

            handler = self.registry.get_executor(node.node_type)
            if handler is None:
                raise DAGExecutionError(f"No executor registered for node type '{node.node_type}'")

            try:
                output = await handler(target_inputs[node_id])
            except Exception as e:
                raise DAGExecutionError(f"Node '{node.id}' failed: {e}") from e

            results[node.id] = output

            # Push outputs to downstream targets
            if node_id in edge_map:
                for src_port, tgt_node, tgt_port, condition in edge_map[node_id]:
                    value = output.get(src_port)
                    if value is None:
                        continue
                    if condition:
                        if not self._eval_condition(condition, {"value": value, "inputs": target_inputs[node_id]}):
                            continue
                    target_inputs[tgt_node][tgt_port] = value

            # Update in-degree
            if node_id in edge_map:
                for _, tgt_node, _, _ in edge_map[node_id]:
                    in_degree[tgt_node] -= 1
                    if in_degree[tgt_node] == 0:
                        queue.append(tgt_node)

        # Collect global outputs
        global_outs = {}
        for port in graph.global_outputs:
            found = False
            for node in graph.nodes:
                if port.name in results[node.id]:
                    global_outs[port.name] = results[node.id][port.name]
                    found = True
                    break
            if not found:
                raise DAGExecutionError(f"Global output port '{port.name}' not produced by any node")

        return global_outs

    def _find_entry_node(self, graph: DAGGraph) -> str:
        targets = {edge.target_node for edge in graph.edges}
        for node in graph.nodes:
            if node.id not in targets:
                return node.id
        raise DAGExecutionError("Cannot determine entry node")

    @staticmethod
    def _eval_condition(expr: str, context: dict) -> bool:
        return bool(eval(expr, {"__builtins__": {}}, context))
