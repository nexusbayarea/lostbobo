from __future__ import annotations

from abc import ABC, abstractmethod

from backend.core.sdk.plugin_manifest import PluginManifest


class BasePlugin(ABC):
    manifest: PluginManifest

    @abstractmethod
    async def register(self, kernel) -> None:
        """
        Register capabilities + DAG nodes.
        """
        raise NotImplementedError
