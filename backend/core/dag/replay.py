"""
Deterministic replay of DAG executions.
"""

from __future__ import annotations

import copy
from typing import Any

from backend.core.dag.models import DAGGraph
from backend.core.sdk.registries.dag_registry import DAGRegistry


class DAGReplayRecorder:
    """
    Records the input/output of every node during execution.
    """

    def __init__(self):
        self.trace: dict[str, dict[str, Any]] = {}  # node_id -> {"inputs": ..., "outputs": ...}

    def record(self, node_id: str, inputs: dict[str, Any], outputs: dict[str, Any]):
        self.trace[node_id] = {
            "inputs": copy.deepcopy(inputs),
            "outputs": copy.deepcopy(outputs),
        }

    def get_inputs(self, node_id: str) -> dict[str, Any] | None:
        entry = self.trace.get(node_id)
        return entry["inputs"] if entry else None


class DAGReplayer:
    """
    Replays a DAG using previously recorded inputs, bypassing actual execution.
    """

    def __init__(self, recorder: DAGReplayRecorder, registry: DAGRegistry):
        self.recorder = recorder
        self.registry = registry

    async def replay(self, graph: DAGGraph, run_id: str) -> dict[str, Any]:
        global_outs = {}
        for port in graph.global_outputs:
            for node in graph.nodes:
                if node.id in self.recorder.trace and port.name in self.recorder.trace[node.id]["outputs"]:
                    global_outs[port.name] = self.recorder.trace[node.id]["outputs"][port.name]
                    break
        return global_outs
