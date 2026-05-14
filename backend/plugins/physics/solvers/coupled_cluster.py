from __future__ import annotations

from backend.plugins.physics.schemas.molecule import MoleculeInput, MoleculeOutput
from backend.plugins.physics.solvers.schrodinger import solve_schrodinger


async def solve_coupled_cluster(
    molecule: MoleculeInput,
    method: str = "ccsd",
    backend: str = "psi4",
) -> MoleculeOutput:
    molecule.method = method
    return await solve_schrodinger(molecule, backend=backend)
