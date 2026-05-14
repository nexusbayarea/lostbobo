from __future__ import annotations

from backend.core.sdk.registries.capability_registry import CapabilityRegistry
from backend.core.sdk.registries.dag_registry import DAGNodeRegistry
from backend.plugins.physics.plugin import plugin


async def test_physics_plugin_registers_capabilities():
    cap_registry = CapabilityRegistry()
    dag_registry = DAGNodeRegistry()

    class MockKernel:
        def __init__(self):
            self.capability_registry = cap_registry
            self.dag_registry = dag_registry

    kernel = MockKernel()
    await plugin.register(kernel)

    assert "physics.solve" in cap_registry.registered_capabilities
    assert "physics.simulate" in cap_registry.registered_capabilities
    assert "physics.backend.status" in cap_registry.registered_capabilities
    assert "beam.solve" in dag_registry.registered_nodes
    assert "schrodinger.solve" in dag_registry.registered_nodes


async def test_physics_solve_with_backend_status():
    cap_registry = CapabilityRegistry()
    dag_registry = DAGNodeRegistry()

    class MockKernel:
        def __init__(self):
            self.capability_registry = cap_registry
            self.dag_registry = dag_registry

    kernel = MockKernel()
    await plugin.register(kernel)

    result = await cap_registry.invoke("physics.backend.status", {})
    assert "backends" in result
    assert "pyscf" in result["backends"]
    assert "psi4" in result["backends"]
    assert "orca" in result["backends"]
