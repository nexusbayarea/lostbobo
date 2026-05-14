from __future__ import annotations

from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone

from backend.core.sdk.runtime.plugin_context import PluginContext
from backend.core.sdk.abi.lifecycle import PluginState


class PluginAlreadyRegistered(Exception):
    pass


class PluginNotFound(Exception):
    pass


@dataclass
class PluginRecord:
    context: PluginContext
    installed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_health_check: Optional[datetime] = None
    health_status: str = "unknown"


class PluginRegistry:
    def __init__(self):
        self._plugins: Dict[str, PluginRecord] = {}

    def register(self, ctx: PluginContext) -> None:
        if ctx.plugin_name in self._plugins:
            raise PluginAlreadyRegistered(f"Plugin '{ctx.plugin_name}' already registered")
        self._plugins[ctx.plugin_name] = PluginRecord(context=ctx)

    def unregister(self, plugin_name: str) -> None:
        self._plugins.pop(plugin_name, None)

    def get(self, plugin_name: str) -> Optional[PluginRecord]:
        return self._plugins.get(plugin_name)

    def get_context(self, plugin_name: str) -> Optional[PluginContext]:
        record = self._plugins.get(plugin_name)
        return record.context if record else None

    def list_running(self) -> list[str]:
        return [
            name
            for name, record in self._plugins.items()
            if record.context.lifecycle.current_state == PluginState.RUNNING
        ]

    def list_by_state(self, state: PluginState) -> list[str]:
        return [name for name, record in self._plugins.items() if record.context.lifecycle.current_state == state]

    def update_health(self, plugin_name: str, status: str) -> None:
        record = self._plugins.get(plugin_name)
        if record:
            record.health_status = status
            record.last_health_check = datetime.now(timezone.utc)

    @property
    def all_plugins(self) -> Dict[str, PluginRecord]:
        return dict(self._plugins)

    @property
    def count(self) -> int:
        return len(self._plugins)
