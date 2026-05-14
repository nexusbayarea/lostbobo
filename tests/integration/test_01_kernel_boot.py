from __future__ import annotations

import pytest

from backend.core.sdk.abi.lifecycle import PluginState


@pytest.mark.asyncio
async def test_kernel_initializes(kernel):
    assert kernel.capability_registry is not None
    assert kernel.dag_registry is not None
    assert kernel.plugin_registry is not None
    assert kernel.scheduler is not None


@pytest.mark.asyncio
async def test_plugins_discovered(kernel):
    running = kernel.plugin_registry.list_running()
    assert "physics" in running
    assert "forecasting" in running


@pytest.mark.asyncio
async def test_physics_capabilities_registered(kernel):
    caps = kernel.capability_registry.registered_capabilities
    assert "physics.solve" in caps
    assert "physics.simulate" in caps
    assert "physics.backend.status" in caps


@pytest.mark.asyncio
async def test_forecasting_capabilities_registered(kernel):
    caps = kernel.capability_registry.registered_capabilities
    assert "forecast.generate" in caps
    assert "forecast.calibrate" in caps


@pytest.mark.asyncio
async def test_physics_dag_nodes_registered(kernel):
    nodes = kernel.dag_registry.registered_nodes
    assert "beam.solve" in nodes
    assert "schrodinger.solve" in nodes


@pytest.mark.asyncio
async def test_plugin_lifecycle_states(kernel):
    for name in kernel.plugin_registry.list_running():
        record = kernel.plugin_registry.get(name)
        assert record.context.lifecycle.current_state == PluginState.RUNNING


@pytest.mark.asyncio
async def test_plugin_manifests_are_valid(kernel):
    for name in kernel.plugin_registry.list_running():
        record = kernel.plugin_registry.get(name)
        manifest = record.context.plugin_instance.manifest
        assert manifest.name == name
        assert manifest.version is not None
        assert len(manifest.capabilities) > 0
