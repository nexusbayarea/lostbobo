from __future__ import annotations


class ExecutionRuntime:
    async def execute_capability(
        self,
        kernel,
        capability: str,
        payload: dict,
    ):
        return await kernel.capabilities.invoke(
            capability,
            payload,
        )

    async def execute_dag_node(
        self,
        kernel,
        node_type: str,
        payload: dict,
    ):
        return await kernel.dag.execute_node(
            node_type,
            payload,
        )
