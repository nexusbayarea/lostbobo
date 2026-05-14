from __future__ import annotations

from backend.plugins.physics.schemas.molecule import MoleculeInput, MoleculeOutput
from backend.plugins.physics.solvers.schrodinger import solve_schrodinger

KNOWN_FUNCTIONALS: dict[str, str] = {
    "b3lyp": "b3lyp",
    "pbe": "pbe",
    "pbe0": "pbe0",
    "wb97xd": "wb97xd",
    "tpss": "tpss",
}


async def solve_dft(
    molecule: MoleculeInput,
    functional: str = "b3lyp",
    backend: str = "pyscf",
) -> MoleculeOutput:
    molecule.method = "dft"
    molecule.options["functional"] = KNOWN_FUNCTIONALS.get(functional, functional)
    return await solve_schrodinger(molecule, backend=backend)
