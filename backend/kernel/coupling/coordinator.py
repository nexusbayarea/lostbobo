from typing import Any

import structlog

from backend.core.supabase_job_store import SupabaseJobStore
from backend.kernel.abi.plugin import PhysicsPlugin
from backend.kernel.kernel import Kernel

log = structlog.get_logger(__name__)


class StateExchange:
    def __init__(self, kernel):
        self.kernel = kernel

    def map(self, states: dict[str, Any]) -> dict[str, Any]:
        return states


class CouplingConvergence:
    def evaluate(self, states: dict[str, Any]) -> bool:
        return True


class CouplingCoordinator:
    """Orchestrates tightly coupled multi-physics simulations."""

    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.plugins: list[PhysicsPlugin] = []
        self.exchange = StateExchange(kernel)
        self.convergence = CouplingConvergence()
        self.supabase = SupabaseJobStore()

    def register_plugin(self, plugin: PhysicsPlugin):
        self.plugins.append(plugin)

    async def execute_timestep(self, dt: float, context: dict[str, Any]) -> dict[str, Any]:
        job_id = context.get("job_id")
        states = {p.name: await p.export_state() for p in self.plugins}
        converged = False
        iteration = 0
        max_iterations = 20

        while not converged and iteration < max_iterations:
            exchanged = self.exchange.map(states)
            for plugin in self.plugins:
                await plugin.step(dt, exchanged)
            states = {p.name: await p.export_state() for p in self.plugins}
            converged = self.convergence.evaluate(states)
            iteration += 1
            await self.kernel.services["telemetry"].publish(
                {"simulation_id": job_id, "metric": "coupling_iteration", "value": iteration, "converged": converged}
            )

        return states
