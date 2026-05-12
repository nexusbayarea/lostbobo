import asyncio
from typing import Any
from uuid import uuid4

from backend.core.dag.lineage.lineage import DAGLineage
from backend.core.dag.models import DAGGraph
from backend.core.dag.replay.replay import DAGReplayer, DAGReplayRecorder
from backend.core.dag.runtime.execution_planner import ExecutionPlanner
from backend.core.scheduler.kernel_scheduler import KernelScheduler
from backend.core.scheduler.scheduler_models import ResourceRequest, Workload, WorkloadPriority, WorkloadType


class DAGRuntime:
    def __init__(self, kernel):
        self.kernel = kernel
        self.planner = ExecutionPlanner()
        self.scheduler: KernelScheduler = kernel.scheduler
        self.dag_registry = kernel.dag_registry
        self.lineage = DAGLineage(kernel.lineage_syscalls)  # Assume kernel exposes lineage syscalls
        self.replay_recorder = DAGReplayRecorder()
        self.replayer = DAGReplayer(self.replay_recorder, self.dag_registry)

    async def execute(self, dag: DAGGraph, tenant_id: str, global_inputs: dict[str, Any]) -> dict[str, Any]:
        run_id = str(uuid4())
        await self.lineage.record_graph_start(dag.id, run_id)

        # Build levels
        levels = self.planner.execution_plan(dag)

        # Execution state tracking
        node_states: dict[str, str] = {n.id: "PENDING" for n in dag.nodes}
        outputs: dict[str, Any] = {}
        global_outputs: dict[str, Any] = {}

        for node_ids in levels:
            tasks = []
            for nid in node_ids:
                node = next(n for n in dag.nodes if n.id == nid)
                node_states[nid] = "READY"
                tasks.append(self._execute_node(dag, node, node_states, outputs, run_id, tenant_id, global_inputs))
            await asyncio.gather(*tasks)

        if dag.nodes:
            final_node = dag.nodes[-1]
            if final_node.id in outputs:
                global_outputs = outputs[final_node.id]

        await self.lineage.record_graph_end(dag.id, run_id, global_outputs)
        return global_outputs

    async def _execute_node(self, dag, node, states, outputs, run_id, tenant_id, global_inputs):
        await self.lineage.record_node_start(dag.id, run_id, node.id)

        # Prepare inputs (simple mapping from previous outputs)
        inputs = global_inputs.copy()
        for edge in dag.edges:
            if edge.target_node == node.id:
                inputs[edge.target_port] = outputs.get(edge.source_node, {}).get(edge.source_port)

        workload = Workload(
            tenant_id=tenant_id,
            plugin_name="unknown",  # Simplified
            workload_type=WorkloadType.DAG,
            priority=WorkloadPriority.NORMAL,
            resources=ResourceRequest(
                cpu_cores=node.resources.get("cpu_cores", 1.0) if node.resources else 1.0,
                memory_mb=node.resources.get("memory_mb", 1024) if node.resources else 1024,
            ),
            dag_id=dag.id,
            dag_node_id=node.id,
        )

        sched_result = await self.scheduler.schedule(workload)
        if sched_result["status"] != "accepted":
            states[node.id] = "FAILED"
            raise RuntimeError(f"Node {node.id} rejected by scheduler")

        states[node.id] = "RUNNING"
        try:
            executor = self.dag_registry.get_executor(node.node_type)
            output = await executor(inputs)
            outputs[node.id] = output
            self.replay_recorder.record(node.id, inputs, output)
            states[node.id] = "COMPLETED"
            await self.lineage.record_node_end(dag.id, run_id, node.id, output, 0.0)
        finally:
            await self.scheduler.release_resources(workload)
