from __future__ import annotations

import pytest

from backend.core.sdk.registries.capability_registry import (
    CapabilityNotFoundError,
    CapabilityPermissionDeniedError,
)


@pytest.mark.asyncio
async def test_registry_invoke_success(kernel):
    result = await kernel.capability_registry.invoke(
        "physics.backend.status", {}, tenant_id="test-lab-1"
    )
    assert "backends" in result
    assert "pyscf" in result["backends"]


@pytest.mark.asyncio
async def test_registry_invoke_nonexistent_capability(kernel):
    with pytest.raises(CapabilityNotFoundError):
        await kernel.capability_registry.invoke("nonexistent.capability", {})


@pytest.mark.asyncio
async def test_registry_invocation_history(kernel):
    await kernel.capability_registry.invoke("physics.backend.status", {})
    history = kernel.capability_registry.get_invocation_history(
        "physics.backend.status"
    )
    assert len(history) >= 1
    assert history[-1].status == "success"
    assert history[-1].inputs_hash is not None
    assert history[-1].outputs_hash is not None


@pytest.mark.asyncio
async def test_registry_tenant_isolation(kernel):
    kernel.capability_registry.set_tenant_capabilities(
        "evil-tenant", {"physics.backend.status"}
    )
    await kernel.capability_registry.invoke(
        "physics.backend.status", {}, tenant_id="evil-tenant"
    )
    with pytest.raises(CapabilityPermissionDeniedError):
        await kernel.capability_registry.invoke(
            "physics.solve",
            {"molecule": {}, "backend": "pyscf"},
            tenant_id="evil-tenant",
        )


@pytest.mark.asyncio
async def test_registry_input_hashing(kernel, water_molecule):
    hash1 = kernel.capability_registry._hash_payload(water_molecule)
    reordered = {
        "spin_multiplicity": 1,
        "atoms": water_molecule["atoms"],
        "basis_set": {"name": "sto-3g"},
        "method": "hf",
        "charge": 0,
    }
    hash2 = kernel.capability_registry._hash_payload(reordered)
    assert hash1 == hash2
