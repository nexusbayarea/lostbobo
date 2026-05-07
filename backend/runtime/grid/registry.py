"""Experiment Registry — tracks all experiments and lineage."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Experiment:
    experiment_id: str
    name: str
    description: str
    objective: str
    owner: str
    dataset_version: str
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


class ExperimentRegistry:
    def __init__(self, kernel: Any = None):
        self.kernel = kernel
        self.experiments: dict[str, Experiment] = {}

    async def register(self, name: str, description: str, objective: str, owner: str, dataset_version: str) -> str:
        exp_id = f"exp_{int(datetime.utcnow().timestamp() * 1000)}"
        exp = Experiment(
            experiment_id=exp_id,
            name=name,
            description=description,
            objective=objective,
            owner=owner,
            dataset_version=dataset_version,
            created_at=datetime.utcnow(),
        )
        self.experiments[exp_id] = exp
        return exp_id

    async def get(self, experiment_id: str) -> Experiment | None:
        return self.experiments.get(experiment_id)
