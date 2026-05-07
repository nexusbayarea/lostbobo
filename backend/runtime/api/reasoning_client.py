"""Remote Reasoning via LLM API (DeepSeek / equivalent)."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator


async def deepseek_api_call(prompt: str, model: str = "deepseek-v3", stream: bool = True) -> AsyncGenerator[str, None]:
    """Stream tokens from remote LLM API (placeholder)."""
    # Placeholder - replace with actual API call
    words = prompt.split()[:10]
    for word in words:
        yield word + " "
        await asyncio.sleep(0.05)
