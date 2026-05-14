from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from backend.core.sdk.abi.plugin_manifest import PluginManifest
from backend.core.sdk.runtime.plugin_context import PluginContext


class BasePlugin(ABC):
    manifest: PluginManifest

    @abstractmethod
    async def register(self, kernel: Any) -> None: ...

    async def health_check(self) -> bool:
        return True

    async def shutdown(self) -> None:
        pass

    async def pre_boot(self, context: PluginContext) -> None:
        pass

    async def post_boot(self, context: PluginContext) -> None:
        pass
