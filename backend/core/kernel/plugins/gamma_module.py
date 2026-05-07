"""Gamma Module Standard Interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class GammaModule(ABC):
    """All domain-specific modules must implement this."""

    name: str
    domain: str

    @abstractmethod
    async def simulate(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run simulation with uncertainty."""
        ...

    @abstractmethod
    async def predict(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Probabilistic prediction."""
        ...

    @abstractmethod
    async def update_state(self, world_update: dict[str, Any]):
        """Sync with World Brain."""
        ...
