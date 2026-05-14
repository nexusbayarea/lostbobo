from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from backend.plugins.physics.schemas.molecule import MoleculeInput, MoleculeOutput


class QuantumBackend(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    async def compute(self, molecule: MoleculeInput) -> MoleculeOutput: ...

    @abstractmethod
    async def is_available(self) -> bool: ...

    @abstractmethod
    async def get_capabilities(self) -> dict[str, Any]: ...
