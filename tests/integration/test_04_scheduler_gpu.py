from __future__ import annotations

import pytest

from backend.core.scheduler.priority_queue import Priority


@pytest.mark.asyncio
async def test_scheduler_schedule_physics(kernel, water_molecule):
    result = await kernel.scheduler.schedule_capability(
        "physics.solve",
        {"molecule": water_molecule, "backend": "pyscf"},
        tenant_id="test-lab-1",
        priority=Priority.NORMAL,
    )
    assert "energy" in result
    assert result["convergence"] is True


@pytest.mark.asyncio
async def test_scheduler_budget_consumed(kernel, water_molecule):
    budget_before = kernel.budget_manager.budgets["test-lab-1"].consumed_credits
    await kernel.scheduler.schedule_capability(
        "physics.solve",
        {"molecule": water_molecule, "backend": "pyscf"},
        tenant_id="test-lab-1",
    )
    budget_after = kernel.budget_manager.budgets["test-lab-1"].consumed_credits
    assert budget_after > budget_before


@pytest.mark.asyncio
async def test_scheduler_budget_exceeded(kernel, water_molecule):
    await kernel.budget_manager.set_budget("broke-tenant", credits=0.0)
    from backend.core.scheduler.budget_manager import BudgetExceededError

    with pytest.raises(BudgetExceededError):
        await kernel.scheduler.schedule_capability(
            "physics.solve",
            {"molecule": water_molecule, "backend": "pyscf"},
            tenant_id="broke-tenant",
        )


@pytest.mark.asyncio
async def test_scheduler_queue_stats(kernel):
    stats = await kernel.priority_queue.stats
    assert "depth" in stats
    assert "total_enqueued" in stats
    assert "total_dequeued" in stats
