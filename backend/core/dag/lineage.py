"""
Lineage hooks for DAG execution.
"""

from __future__ import annotations

import time
from typing import Any


class DAGLineage:
    def __init__(self, kernel_lineage):
        self.lineage = kernel_lineage

    async def record_node_start(self, graph_id: str, run_id: str, node_id: str):
        await self.lineage.write_lineage(
            {
                "event": "dag.node.started",
                "graph_id": graph_id,
                "run_id": run_id,
                "node_id": node_id,
                "timestamp": time.time(),
            }
        )

    async def record_node_end(
        self, graph_id: str, run_id: str, node_id: str, output: dict[str, Any], duration_ms: float
    ):
        await self.lineage.write_lineage(
            {
                "event": "dag.node.completed",
                "graph_id": graph_id,
                "run_id": run_id,
                "node_id": node_id,
                "output": output,
                "duration_ms": duration_ms,
                "timestamp": time.time(),
            }
        )

    async def record_graph_start(self, graph_id: str, run_id: str):
        await self.lineage.write_lineage(
            {
                "event": "dag.graph.started",
                "graph_id": graph_id,
                "run_id": run_id,
                "timestamp": time.time(),
            }
        )

    async def record_graph_end(self, graph_id: str, run_id: str, global_outputs: dict[str, Any]):
        await self.lineage.write_lineage(
            {
                "event": "dag.graph.completed",
                "graph_id": graph_id,
                "run_id": run_id,
                "global_outputs": global_outputs,
                "timestamp": time.time(),
            }
        )
