from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from backend.core.sdk.abi.plugin_manifest import PluginManifest
from backend.core.sdk.runtime.plugin_context import PluginContext


class SandboxAdapter(ABC):
    @abstractmethod
    async def launch(self, manifest: PluginManifest, context: PluginContext) -> Any: ...

    @abstractmethod
    async def stop(self, context: PluginContext) -> None: ...


class ProcessAdapter(SandboxAdapter):
    async def launch(self, manifest: PluginManifest, context: PluginContext) -> None:
        return None

    async def stop(self, context: PluginContext) -> None:
        pass


class WasmAdapter(SandboxAdapter):
    async def launch(self, manifest: PluginManifest, context: PluginContext) -> str:
        sandbox_id = f"wasm_{manifest.name}_{id(self)}"
        context.sandbox_handle = sandbox_id
        return sandbox_id

    async def stop(self, context: PluginContext) -> None:
        context.sandbox_handle = None


class KataAdapter(SandboxAdapter):
    async def launch(self, manifest: PluginManifest, context: PluginContext) -> str:
        sandbox_id = f"kata_{manifest.name}_{id(self)}"
        context.sandbox_handle = sandbox_id
        return sandbox_id

    async def stop(self, context: PluginContext) -> None:
        context.sandbox_handle = None


def get_sandbox_adapter(
    manifest: PluginManifest,
) -> SandboxAdapter:
    from backend.core.sdk.abi.plugin_manifest import IsolationTier

    tier = manifest.isolation_tier
    if tier in (IsolationTier.WASM,):
        return WasmAdapter()
    if tier in (IsolationTier.KATA,):
        return KataAdapter()
    return ProcessAdapter()
