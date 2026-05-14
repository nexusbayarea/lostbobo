from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_physics_solve_water(kernel, water_molecule):
    result = await kernel.scheduler.schedule_capability(
        "physics.solve",
        {"molecule": water_molecule, "backend": "pyscf"},
        tenant_id="test-lab-1",
    )
    assert "energy" in result
    assert result["energy_units"] == "hartree"
    assert result["convergence"] is True
    assert -80 < result["energy"] < -70


@pytest.mark.asyncio
async def test_physics_solve_methane(kernel):
    methane = {
        "atoms": [
            {"symbol": "C", "x": 0.000, "y": 0.000, "z": 0.000},
            {"symbol": "H", "x": 0.629, "y": 0.629, "z": 0.629},
            {"symbol": "H", "x": -0.629, "y": -0.629, "z": 0.629},
            {"symbol": "H", "x": 0.629, "y": -0.629, "z": -0.629},
            {"symbol": "H", "x": -0.629, "y": 0.629, "z": -0.629},
        ],
        "charge": 0,
        "spin_multiplicity": 1,
        "basis_set": {"name": "sto-3g"},
        "method": "hf",
    }
    result = await kernel.scheduler.schedule_capability(
        "physics.solve",
        {"molecule": methane, "backend": "pyscf"},
        tenant_id="test-lab-1",
    )
    assert result["convergence"] is True
    assert -45 < result["energy"] < -35


@pytest.mark.asyncio
async def test_physics_backend_status(kernel):
    result = await kernel.scheduler.schedule_capability(
        "physics.backend.status", {}, tenant_id="test-lab-1"
    )
    assert "backends" in result
    assert result["backends"]["pyscf"]["available"] is True


@pytest.mark.asyncio
async def test_physics_molecule_formula(kernel, water_molecule):
    from backend.plugins.physics.schemas.molecule import MoleculeInput

    mol = MoleculeInput(**water_molecule)
    assert mol.formula == "H2O"
