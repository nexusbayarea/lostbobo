from __future__ import annotations

import asyncio
import time
from typing import Any

from backend.plugins.physics.backends.base import QuantumBackend
from backend.plugins.physics.schemas.molecule import MoleculeInput, MoleculeOutput


class PySCFAdapter(QuantumBackend):
    @property
    def name(self) -> str:
        return "pyscf"

    async def is_available(self) -> bool:
        try:
            import pyscf  # noqa: F401

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
            backend="pyscf",
            metadata={
                "method": molecule.method,
                "basis": molecule.basis_set.name,
            },
        )

    def _compute_sync(self, molecule: MoleculeInput) -> dict[str, Any]:
        from pyscf import dft, gto, scf

        mol = gto.M(
            atom=[[a.symbol, (a.x, a.y, a.z)] for a in molecule.atoms],
            basis=molecule.basis_set.name,
            charge=molecule.charge,
            spin=molecule.spin_multiplicity - 1,
        )
        if molecule.method.lower() == "hf":
            mf = scf.RHF(mol)
        elif molecule.method.lower() == "dft":
            mf = dft.RKS(mol)
            mf.xc = molecule.options.get("functional", "b3lyp")
        else:
            raise ValueError(f"Unsupported method: {molecule.method}")
        mf.kernel()
        return {
            "energy": float(mf.e_tot),
            "converged": mf.converged,
            "iterations": mf.iterations,
        }

    async def get_capabilities(self) -> dict[str, Any]:
        return {
            "methods": ["hf", "dft"],
            "dft_functionals": ["b3lyp", "pbe", "pbe0"],
            "basis_sets": ["sto-3g", "6-31g", "cc-pvdz", "cc-pvtz"],
        }
