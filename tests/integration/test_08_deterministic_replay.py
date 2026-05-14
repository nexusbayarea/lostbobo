from __future__ import annotations

import pytest

from backend.core.sdk.registries.capability_registry import ExecutionContext


@pytest.mark.asyncio
async def test_same_seed_same_output(kernel, water_molecule):
    ctx = ExecutionContext(seed=12345)
    r1 = await kernel.capability_registry.invoke(
        "physics.solve",
        {"molecule": water_molecule, "backend": "pyscf"},
        execution_context=ctx,
    )
    r2 = await kernel.capability_registry.invoke(
        "physics.solve",
        {"molecule": water_molecule, "backend": "pyscf"},
        execution_context=ctx,
    )
    assert r1["energy"] == r2["energy"]


@pytest.mark.asyncio
async def test_different_seed_same_deterministic(kernel, water_molecule):
    ctx1 = ExecutionContext(seed=42)
    ctx2 = ExecutionContext(seed=99)
    r1 = await kernel.capability_registry.invoke(
        "physics.solve",
        {"molecule": water_molecule, "backend": "pyscf"},
        execution_context=ctx1,
    )
    r2 = await kernel.capability_registry.invoke(
        "physics.solve",
        {"molecule": water_molecule, "backend": "pyscf"},
        execution_context=ctx2,
    )
    assert r1["energy"] == r2["energy"]


@pytest.mark.asyncio
async def test_invocation_record_hashes_match(kernel, water_molecule):
    await kernel.capability_registry.invoke(
        "physics.solve",
        {"molecule": water_molecule, "backend": "pyscf"},
    )
    history = kernel.capability_registry.get_invocation_history("physics.solve")
    record = history[-1]
    expected_input_hash = kernel.capability_registry._hash_payload(
        {"molecule": water_molecule, "backend": "pyscf"}
    )
    assert record.inputs_hash == expected_input_hash
    assert record.outputs_hash is not None
    assert record.status == "success"
