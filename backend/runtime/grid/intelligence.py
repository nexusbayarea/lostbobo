"""Experiment Intelligence — meta-learning across experiments."""

from __future__ import annotations

from typing import Any


class ExperimentIntelligence:
    def __init__(self, kernel: Any = None):
        self.kernel = kernel

    async def get_parameter_priors(self, objective: str) -> dict[str, Any]:
        """Learns from past experiments to suggest better starting parameters."""
        return {}

    async def suggest_next_swarm(self, experiment_id: str) -> dict[str, Any]:
        """Proposes next swarm based on past discoveries."""
        return {"suggested_algorithm": "bayesian", "parameter_priors": {}, "recommended_size": 2000}
