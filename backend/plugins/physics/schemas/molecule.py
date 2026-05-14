from __future__ import annotations

from collections import Counter
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Atom(BaseModel):
    symbol: str = Field(pattern=r"^[A-Z][a-z]?$")
    x: float
    y: float
    z: float
    charge: float = 0.0


class BasisSet(BaseModel):
    name: str = "sto-3g"


class MoleculeInput(BaseModel):
    atoms: list[Atom]
    charge: int = 0
    spin_multiplicity: int = 1
    basis_set: BasisSet = Field(default_factory=BasisSet)
    method: str = "hf"
    options: dict[str, Any] = Field(default_factory=dict)

    @field_validator("spin_multiplicity")
    @classmethod
    def spin_must_be_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("spin_multiplicity must be >= 1")
        return v

    @property
    def formula(self) -> str:
        counts = Counter(atom.symbol for atom in self.atoms)
        return "".join(f"{sym}{counts[sym] if counts[sym] > 1 else ''}" for sym in sorted(counts))


class MoleculeOutput(BaseModel):
    energy: float
    energy_units: str = "hartree"
    convergence: bool = True
    iterations: int = 0
    wall_time_seconds: float = 0.0
    backend: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
