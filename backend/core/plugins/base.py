from __future__ import annotations

from abc import ABC, abstractmethod

from .manifests import PluginManifest


class BasePlugin(ABC):
    """All plugins must inherit this contract."""

    manifest: PluginManifest

    @abstractmethod
    async def load(self) -> None:
        """Load plugin code and resources."""

    @abstractmethod
    async def initialize(self) -> None:
        """Runtime initialization (capabilities validated here)."""

    @abstractmethod
    async def register(self) -> None:
        """Register with PluginRegistry and AgentRuntime."""

    @abstractmethod
    async def shutdown(self) -> None:
        """Graceful shutdown."""

    @abstractmethod
    async def recover(self, reason: str) -> None:
        """Recovery after failure."""
