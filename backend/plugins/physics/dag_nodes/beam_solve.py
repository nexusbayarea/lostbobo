from __future__ import annotations

from typing import Any

from backend.plugins.physics.schemas.molecule import MoleculeInput
from backend.plugins.physics.solvers.schrodinger import solve_schrodinger


async def beam_solve(inputs: dict[str, Any]) -> dict[str, Any]:
    molecule = MoleculeInput(**inputs["molecule"])
    backend = inputs.get("backend", "pyscf")
    result = await solve_schrodinger(molecule, backend=backend)
    return {
        "energy": result.energy,
        "energy_units": result.energy_units,
        "convergence": result.convergence,
        "wall_time_seconds": result.wall_time_seconds,
        "backend": result.backend,
        "formula": molecule.formula,
    }
