from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_every_invocation_has_lineage_record(kernel):
    await kernel.capability_registry.invoke("physics.backend.status", {})
    history = kernel.capability_registry.get_invocation_history(
        "physics.backend.status"
    )
    assert len(history) >= 1
    record = history[-1]
    assert record.invocation_id is not None
    assert record.capability == "physics.backend.status"
    assert record.started_at is not None
    assert record.finished_at is not None
    assert record.status == "success"


@pytest.mark.asyncio
async def test_lineage_includes_plugin_info(kernel, water_molecule):
    await kernel.capability_registry.invoke(
        "physics.solve",
        {"molecule": water_molecule, "backend": "pyscf"},
    )
    history = kernel.capability_registry.get_invocation_history("physics.solve")
    record = history[-1]
    assert record.plugin_name == "physics"


@pytest.mark.asyncio
async def test_lineage_inputs_outputs_hashed(kernel, water_molecule):
    await kernel.capability_registry.invoke(
        "physics.solve",
        {"molecule": water_molecule, "backend": "pyscf"},
    )
    history = kernel.capability_registry.get_invocation_history("physics.solve")
    record = history[-1]
    assert len(record.inputs_hash) == 64
    assert len(record.outputs_hash) == 64


@pytest.mark.asyncio
async def test_lineage_deterministic_flag(kernel, water_molecule):
    await kernel.capability_registry.invoke(
        "physics.solve",
        {"molecule": water_molecule, "backend": "pyscf"},
    )
    history = kernel.capability_registry.get_invocation_history("physics.solve")
    record = history[-1]
    assert record.deterministic is True


@pytest.mark.asyncio
async def test_lineage_failed_invocation_recorded(kernel):
    try:
        await kernel.capability_registry.invoke(
            "forecast.generate",
            {"model": "nonexistent_model", "payload": {}},
        )
    except ValueError:
        pass
    history = kernel.capability_registry.get_invocation_history("forecast.generate")
    assert history[-1].status in {"error", "pending"}
