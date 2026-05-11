from __future__ import annotations

from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

CapabilityHandler = Callable[[dict], Awaitable[Any]]


class CapabilityRegistry:
    def __init__(self):
        self._handlers = {}
        self._graph = defaultdict(set)

    def register(self, capability: str, handler: CapabilityHandler, plugin_name: str):
        self._handlers[capability] = {
            "handler": handler,
            "plugin": plugin_name,
        }

    async def invoke(self, capability: str, payload: dict):
        if capability not in self._handlers:
            raise KeyError(f"Unknown capability: {capability}")
        return await self._handlers[capability]["handler"](payload)

    def capability_graph(self):
        return self._handlers
