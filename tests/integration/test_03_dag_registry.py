from __future__ import annotations

import pytest

from backend.core.sdk.registries.dag_registry import DAGNodeNotFoundError


@pytest.mark.asyncio
async def test_dag_node_registered(kernel):
    assert "beam.solve" in kernel.dag_registry.registered_nodes
    assert "schrodinger.solve" in kernel.dag_registry.registered_nodes


@pytest.mark.asyncio
async def test_dag_node_nonexistent(kernel):
    with pytest.raises(DAGNodeNotFoundError):
        await kernel.dag_registry.execute("nonexistent.node", {})


@pytest.mark.asyncio
async def test_dag_node_metadata(kernel):
    entry = kernel.dag_registry.get_node("beam.solve")
    assert entry.plugin_name == "physics"
    assert entry.deterministic is True
    assert entry.idempotent is True
