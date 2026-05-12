from __future__ import annotations

from typing import Any

from backend.runtime.scientific.adapters.base import ScientificAdapter, SolverConfig


class MFEMAdapter(ScientificAdapter):
    async def validate(self, config: SolverConfig) -> bool:
        required = ["dimension", "mesh_file"]
        return all(p in config.parameters for p in required)

    async def run(self, config: SolverConfig, inputs: dict[str, Any]) -> dict[str, Any]:
        try:
            import mfem
        except ImportError:
            return {
                "error": "mfem not available",
                "solver_type": "mfem",
                "parameters": config.parameters,
            }

        mesh_file = config.parameters.get("mesh_file")
        if config.mesh_data:
            with open("/tmp/mesh.mfem", "wb") as f:
                f.write(config.mesh_data)
            mesh_file = "/tmp/mesh.mfem"

        if not mesh_file:
            raise ValueError("No mesh file provided")

        mesh = mfem.Mesh(mesh_file, 1, 1)
        order = config.parameters.get("order", 1)
        fec = mfem.H1_FECollection(order, mesh.Dimension())
        fes = mfem.FiniteElementSpace(mesh, fec)

        a = mfem.BilinearForm(fes)
        a.AddDomainIntegrator(mfem.DiffusionIntegrator(mfem.ConstantCoefficient(1.0)))
        a.Assemble()

        b = mfem.LinearForm(fes)
        b.AddDomainIntegrator(mfem.DomainLFIntegrator(mfem.ConstantCoefficient(1.0)))
        b.Assemble()

        mat = a.Finalize()
        rhs = b
        sol = mfem.GridFunction(fes)
        mat.Inverse().Mult(rhs, sol)

        result = sol.Max()

        if config.parameters.get("save_glvis", False):
            sol_sock = mfem.socketstream("localhost", 19916)
            sol_sock.precision(8)
            sol_sock.send_solution(mesh, sol)

        return {
            "max_displacement": float(result),
            "mesh_elements": mesh.GetNE(),
        }
