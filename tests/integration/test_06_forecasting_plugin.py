from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_forecast_generate_weather(kernel, weather_forecast_payload):
    result = await kernel.scheduler.schedule_capability(
        "forecast.generate",
        weather_forecast_payload,
        tenant_id="test-lab-1",
    )
    assert isinstance(result, dict)
    assert "mean" in result


@pytest.mark.asyncio
async def test_forecast_generate_ev(kernel):
    result = await kernel.scheduler.schedule_capability(
        "forecast.generate",
        {"model": "ev", "payload": {"region": "US", "horizon": "30d"}},
        tenant_id="test-lab-1",
    )
    assert isinstance(result, dict)
    assert result["mean"] == 0.35


@pytest.mark.asyncio
async def test_forecast_generate_market(kernel):
    result = await kernel.scheduler.schedule_capability(
        "forecast.generate",
        {"model": "market", "payload": {"symbol": "AAPL", "horizon": "7d"}},
        tenant_id="test-lab-1",
    )
    assert isinstance(result, dict)
    assert "mean" in result


@pytest.mark.asyncio
async def test_forecast_generate_wildfire(kernel):
    result = await kernel.scheduler.schedule_capability(
        "forecast.generate",
        {"model": "wildfire", "payload": {"region": "CA", "season": "dry"}},
        tenant_id="test-lab-1",
    )
    assert isinstance(result, dict)
    assert result["mean"] == 0.15


@pytest.mark.asyncio
async def test_forecast_unknown_model_raises(kernel):
    with pytest.raises(ValueError):
        await kernel.scheduler.schedule_capability(
            "forecast.generate",
            {"model": "crystal_ball", "payload": {}},
            tenant_id="test-lab-1",
        )


@pytest.mark.asyncio
async def test_forecast_calibrate_registered(kernel):
    assert "forecast.calibrate" in kernel.capability_registry.registered_capabilities


@pytest.mark.asyncio
async def test_forecast_prompt_generation(kernel):
    result = await kernel.capability_registry.invoke(
        "forecast.generate_prompt",
        {"domain": "weather", "template": "default"},
        tenant_id="test-lab-1",
    )
    assert isinstance(result, str)
    assert len(result) > 0
