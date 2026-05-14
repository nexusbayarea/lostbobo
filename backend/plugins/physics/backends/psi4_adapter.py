from __future__ import annotations

import asyncio
import time
from typing import Any

from backend.plugins.physics.backends.base import QuantumBackend
from backend.plugins.physics.schemas.molecule import MoleculeInput, MoleculeOutput


class Psi4Adapter(QuantumBackend):
    @property
    def name(self) -> str:
        return "psi4"

    async def is_available(self) -> bool:
        try:
            import psi4  # noqa: F401

            return True
        except ImportError:
            return False

    async def compute(self, molecule: MoleculeInput) -> MoleculeOutput:
        start = time.monotonic()
        result = await asyncio.get_event_loop().run_in_executor(None, self._compute_sync, molecule)
        return MoleculeOutput(
            energy=result["energy"],
            convergence=result.get("converged", True),
            iterations=result.get("iterations", 0),
            wall_time_seconds=time.monotonic() - start,
            backend="psi4",
            metadata={
                "method": molecule.method,
                "basis": molecule.basis_set.name,
            },
        )

    def _compute_sync(self, molecule: MoleculeInput) -> dict[str, Any]:
        import psi4

        psi4.core.be_quiet()
        psi4.geometry(
            f"{molecule.charge} {molecule.spin_multiplicity}\n"
            + "\n".join(f"{a.symbol} {a.x} {a.y} {a.z}" for a in molecule.atoms)
        )
        psi4.set_options({"basis": molecule.basis_set.name})
        method_map = {"hf": "scf", "dft": "dft"}
        psi4_method = method_map.get(molecule.method.lower(), molecule.method)
        energy = psi4.energy(psi4_method)
        return {
            "energy": float(energy),
            "converged": True,
            "iterations": 0,
        }

    async def get_capabilities(self) -> dict[str, Any]:
        return {
            "methods": ["hf", "dft", "mp2", "ccsd"],
            "dft_functionals": ["b3lyp", "pbe", "pbe0", "wb97xd"],
            "basis_sets": ["sto-3g", "6-31g", "cc-pvdz", "cc-pvtz", "aug-cc-pvqz"],
        }
