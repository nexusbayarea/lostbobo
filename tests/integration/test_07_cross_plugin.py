from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_forecast_then_physics(kernel, water_molecule):
    weather = await kernel.scheduler.schedule_capability(
        "forecast.generate",
        {"model": "weather", "payload": {"location": "San Francisco"}},
        tenant_id="test-lab-1",
    )
    physics = await kernel.scheduler.schedule_capability(
        "physics.solve",
        {"molecule": water_molecule, "backend": "pyscf"},
        tenant_id="test-lab-1",
    )
    assert isinstance(weather, dict)
    assert "energy" in physics


@pytest.mark.asyncio
async def test_both_plugins_use_same_scheduler(kernel):
    await kernel.scheduler.schedule_capability(
        "physics.backend.status", {}, tenant_id="test-lab-1"
    )
    await kernel.scheduler.schedule_capability(
        "forecast.generate",
        {"model": "weather", "payload": {"location": "test"}},
        tenant_id="test-lab-1",
    )
    physics_history = kernel.capability_registry.get_invocation_history(
        "physics.backend.status"
    )
    forecast_history = kernel.capability_registry.get_invocation_history(
        "forecast.generate"
    )
    assert len(physics_history) >= 1
    assert len(forecast_history) >= 1


@pytest.mark.asyncio
async def test_plugins_isolated_budgets(kernel, water_molecule):
    b1_before = kernel.budget_manager.budgets["test-lab-1"].consumed_credits
    b2_before = kernel.budget_manager.budgets["test-lab-2"].consumed_credits
    await kernel.scheduler.schedule_capability(
        "physics.solve",
        {"molecule": water_molecule, "backend": "pyscf"},
        tenant_id="test-lab-1",
    )
    b1_after = kernel.budget_manager.budgets["test-lab-1"].consumed_credits
    b2_after = kernel.budget_manager.budgets["test-lab-2"].consumed_credits
    assert b1_after > b1_before
    assert b2_after == b2_before
