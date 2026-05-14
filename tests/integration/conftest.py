from __future__ import annotations

import asyncio
from typing import AsyncGenerator

import pytest

from tests.integration.fixtures.molecules import WATER
from tests.integration.fixtures.forecast_scenarios import WEATHER_SF


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def kernel() -> AsyncGenerator:
    from backend.core.kernel.kernel import SimHPCKernel

    k = SimHPCKernel()
    await k.budget_manager.set_budget("test-lab-1", credits=10000.0)
    await k.budget_manager.set_budget("test-lab-2", credits=10000.0)
    await k.budget_manager.set_budget("evil-tenant", credits=10.0)
    await k.start()
    yield k
    await k.stop()


@pytest.fixture
def water_molecule():
    return dict(WATER)


@pytest.fixture
def weather_forecast_payload():
    return dict(WEATHER_SF)
