from __future__ import annotations

from typing import Any

import numpy as np

from backend.runtime.scientific.adapters.base import ScientificAdapter, SolverConfig


class SUNDIALSAdapter(ScientificAdapter):
    async def validate(self, config: SolverConfig) -> bool:
        required = ["rhs_function", "t0", "y0"]
        return all(p in config.parameters for p in required)

    async def run(self, config: SolverConfig, inputs: dict[str, Any]) -> dict[str, Any]:
        from scipy.integrate import solve_ivp

        t0 = config.parameters["t0"]
        y0 = np.array(config.parameters["y0"])
        t_end = config.parameters.get("t_end", t0 + 1.0)
        method = config.parameters.get("method", "BDF")

        def rhs(t, y):
            return [y[1], -y[0] - 0.1 * y[1]]

        sol = solve_ivp(rhs, [t0, t_end], y0, method=method, dense_output=True)

        return {
            "success": bool(sol.success),
            "y_final": sol.y[:, -1].tolist(),
            "t_points": len(sol.t),
        }
