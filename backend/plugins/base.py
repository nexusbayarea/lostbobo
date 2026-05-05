"""Plugin base class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class PluginBase(ABC):
    """Abstract base class for all plugins."""

    name: str
    version: str = "0.1.0"
    category: str = "domain"

    @abstractmethod
    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Main execution entrypoint."""
        pass

    async def validate(self, input_data: dict[str, Any]) -> bool:
        """Optional validation hook."""
        return True