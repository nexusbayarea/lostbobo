from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class SolverConfig(BaseModel):
    solver_type: str
    parameters: dict[str, Any] = {}
    mesh_data: bytes | None = None


class ScientificAdapter(ABC):
    @abstractmethod
    async def run(self, config: SolverConfig, inputs: dict[str, Any]) -> dict[str, Any]:
        pass

    @abstractmethod
    async def validate(self, config: SolverConfig) -> bool:
        pass
