from __future__ import annotations

import asyncio

import pytest

from backend.core.sdk.registries.capability_registry import CapabilityTimeoutError


@pytest.mark.asyncio
async def test_capability_timeout(kernel):
    async def slow_handler(payload):
        await asyncio.sleep(10)
        return {"done": True}

    kernel.capability_registry.register(
        "test.slow",
        slow_handler,
        plugin_name="test",
        timeout_seconds=1,
    )
    with pytest.raises(CapabilityTimeoutError):
        await kernel.capability_registry.invoke("test.slow", {})


@pytest.mark.asyncio
async def test_idempotent_retry(kernel):
    call_count = 0

    async def flaky_handler(payload):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise asyncio.TimeoutError("Simulated timeout")
        return {"success": True}

    kernel.capability_registry.register(
        "test.flaky",
        flaky_handler,
        plugin_name="test",
        timeout_seconds=5,
        idempotent=True,
        max_retries=3,
    )
    result = await kernel.capability_registry.invoke("test.flaky", {})
    assert result == {"success": True}
    assert call_count == 3


@pytest.mark.asyncio
async def test_non_idempotent_no_retry(kernel):
    call_count = 0

    async def flaky_handler(payload):
        nonlocal call_count
        call_count += 1
        raise ValueError("Boom")

    kernel.capability_registry.register(
        "test.flaky_non_idempotent",
        flaky_handler,
        plugin_name="test",
        idempotent=False,
        max_retries=5,
    )
    with pytest.raises(ValueError):
        await kernel.capability_registry.invoke("test.flaky_non_idempotent", {})
    assert call_count == 1
