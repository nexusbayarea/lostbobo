from __future__ import annotations

import time
from typing import Any

from backend.plugins.physics.backends.base import QuantumBackend
from backend.plugins.physics.schemas.molecule import MoleculeInput, MoleculeOutput


class OrcaAdapter(QuantumBackend):
    @property
    def name(self) -> str:
        return "orca"

    async def is_available(self) -> bool:
        import shutil

        return shutil.which("orca") is not None

    async def compute(self, molecule: MoleculeInput) -> MoleculeOutput:
        start = time.monotonic()
        import tempfile

        inp = self._build_input(molecule)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".inp", delete=False) as f:
            f.write(inp)
            inp_path = f.name
        import asyncio

        proc = await asyncio.create_subprocess_exec("orca", inp_path, stdout=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
        energy = self._parse_energy(stdout.decode())
        return MoleculeOutput(
            energy=energy,
            wall_time_seconds=time.monotonic() - start,
            backend="orca",
            metadata={"method": molecule.method},
        )

    def _build_input(self, molecule: MoleculeInput) -> str:
        lines = [f"! {molecule.method.upper()} {molecule.basis_set.name}"]
        lines.append(f"* xyz {molecule.charge} {molecule.spin_multiplicity}")
        for a in molecule.atoms:
            lines.append(f"  {a.symbol} {a.x} {a.y} {a.z}")
        lines.append("*")
        return "\n".join(lines)

    @staticmethod
    def _parse_energy(output: str) -> float:
        import re

        match = re.search(r"FINAL SINGLE POINT ENERGY\s+([-\d.]+)", output)
        if match:
            return float(match.group(1))
        return 0.0

    async def get_capabilities(self) -> dict[str, Any]:
        return {
            "methods": ["hf", "dft", "mp2", "ccsd", "ccsdt"],
            "dft_functionals": ["b3lyp", "pbe0", "tpss", "wb97x-d4"],
            "basis_sets": ["sto-3g", "6-31g", "cc-pvdz", "cc-pvtz", "def2-svp"],
        }
