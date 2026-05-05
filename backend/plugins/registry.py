"""Plugin registry — discovers and registers plugins."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.plugins.base import PluginBase


class PluginRegistry:
    """Central plugin registry."""

    _plugins: dict[str, PluginBase] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register a plugin."""

        def decorator(plugin_cls: type[PluginBase]):
            cls._plugins[name] = plugin_cls()
            return plugin_cls

        return decorator

    @classmethod
    def get(cls, name: str) -> PluginBase:
        """Get a plugin by name."""
        return cls._plugins.get(name)

    @classmethod
    def list_all(cls) -> list[str]:
        """List all registered plugins."""
        return list(cls._plugins.keys())