from __future__ import annotations

from backend.plugins.physics.backends.base import QuantumBackend
from backend.plugins.physics.backends.orca_adapter import OrcaAdapter
from backend.plugins.physics.backends.psi4_adapter import Psi4Adapter
from backend.plugins.physics.backends.pyscf_adapter import PySCFAdapter
from backend.plugins.physics.schemas.molecule import MoleculeInput, MoleculeOutput

_backends: dict[str, QuantumBackend] = {}


def _get_backend(name: str) -> QuantumBackend:
    if name not in _backends:
        if name == "pyscf":
            _backends[name] = PySCFAdapter()
        elif name == "psi4":
            _backends[name] = Psi4Adapter()
        elif name == "orca":
            _backends[name] = OrcaAdapter()
        else:
            raise ValueError(f"Unknown backend: {name}")
    return _backends[name]


async def solve_schrodinger(
    molecule: MoleculeInput,
    backend: str = "pyscf",
) -> MoleculeOutput:
    engine = _get_backend(backend)
    if not await engine.is_available():
        raise RuntimeError(f"Backend '{backend}' is not available")
    return await engine.compute(molecule)
