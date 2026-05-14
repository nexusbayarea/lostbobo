from __future__ import annotations

from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import asyncio

CapabilityHandler = Callable[[dict], Awaitable[Any]]


class CapabilityAlreadyRegistered(Exception):
    pass


class CapabilityNotFound(Exception):
    pass


class CapabilityTimeoutError(Exception):
    pass


@dataclass
class CapabilityEntry:
    name: str
    handler: CapabilityHandler
    plugin_name: str
    version: str = "1.0.0"
    deterministic: bool = False
    timeout_seconds: int = 300
    invocation_count: int = 0
    last_invoked: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CapabilityRegistry:
    def __init__(self):
        self._handlers: Dict[str, CapabilityEntry] = {}
        self._graph: Dict[str, set[str]] = defaultdict(set)
        self._lock = asyncio.Lock()

    def register(
        self,
        capability: str,
        handler: CapabilityHandler,
        plugin_name: str,
        version: str = "1.0.0",
        deterministic: bool = False,
        timeout_seconds: int = 300,
        metadata: Dict | None = None,
    ) -> None:
        if capability in self._handlers:
            raise CapabilityAlreadyRegistered(
                f"Capability '{capability}' already registered by '{self._handlers[capability].plugin_name}'"
            )
        self._handlers[capability] = CapabilityEntry(
            name=capability,
            handler=handler,
            plugin_name=plugin_name,
            version=version,
            deterministic=deterministic,
            timeout_seconds=timeout_seconds,
            metadata=metadata or {},
        )

    def unregister(self, capability: str) -> None:
        self._handlers.pop(capability, None)

    def list_by_plugin(self, plugin_name: str) -> list[CapabilityEntry]:
        return [e for e in self._handlers.values() if e.plugin_name == plugin_name]

    async def invoke(
        self,
        capability: str,
        payload: Dict[str, Any],
        timeout_seconds: Optional[int] = None,
        caller_plugin: Optional[str] = None,
    ) -> Any:
        entry = self._handlers.get(capability)
        if not entry:
            raise CapabilityNotFound(f"Capability '{capability}' not registered")

        effective_timeout = timeout_seconds or entry.timeout_seconds

        try:
            result = await asyncio.wait_for(
                entry.handler(payload),
                timeout=effective_timeout,
            )
            entry.invocation_count += 1
            entry.last_invoked = datetime.now(timezone.utc)
            return result
        except asyncio.TimeoutError:
            raise CapabilityTimeoutError(f"Capability '{capability}' timed out after {effective_timeout}s")

    def get_entry(self, capability: str) -> Optional[CapabilityEntry]:
        return self._handlers.get(capability)

    def add_dependency(self, source: str, target: str) -> None:
        self._graph[source].add(target)

    def capability_graph(self) -> Dict[str, set[str]]:
        return dict(self._graph)

    @property
    def registered_capabilities(self) -> list[str]:
        return list(self._handlers.keys())
