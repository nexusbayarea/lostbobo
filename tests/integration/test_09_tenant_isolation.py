from __future__ import annotations

import pytest

from backend.core.sdk.registries.capability_registry import (
    CapabilityPermissionDeniedError,
)


@pytest.mark.asyncio
async def test_tenants_independent_budgets(kernel):
    await kernel.scheduler.schedule_capability(
        "physics.backend.status", {}, tenant_id="test-lab-1"
    )
    await kernel.scheduler.schedule_capability(
        "physics.backend.status", {}, tenant_id="test-lab-2"
    )
    b1 = kernel.budget_manager.budgets["test-lab-1"]
    b2 = kernel.budget_manager.budgets["test-lab-2"]
    assert b1.consumed_credits > 0
    assert b2.consumed_credits > 0


@pytest.mark.asyncio
async def test_tenant_capability_allowlist(kernel):
    kernel.capability_registry.set_tenant_capabilities(
        "restricted-tenant", {"forecast.generate"}
    )
    await kernel.capability_registry.invoke(
        "forecast.generate",
        {"model": "weather", "payload": {"location": "test"}},
        tenant_id="restricted-tenant",
    )
    with pytest.raises(CapabilityPermissionDeniedError):
        await kernel.capability_registry.invoke(
            "physics.solve",
            {"molecule": {}, "backend": "pyscf"},
            tenant_id="restricted-tenant",
        )


@pytest.mark.asyncio
async def test_tenant_budget_reservation(kernel, water_molecule):
    await kernel.budget_manager.set_budget("tiny-tenant", credits=0.0001)
    from backend.core.scheduler.budget_manager import BudgetExceededError

    with pytest.raises(BudgetExceededError):
        await kernel.scheduler.schedule_capability(
            "physics.solve",
            {"molecule": water_molecule, "backend": "pyscf"},
            tenant_id="tiny-tenant",
        )
