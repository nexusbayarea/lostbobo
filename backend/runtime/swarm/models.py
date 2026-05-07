"""Simulation Swarm API - Models."""

from typing import Any

from pydantic import BaseModel


class ForecastingQuestion(BaseModel):
    query: str
    resolution_date: str | None = None
    context_hints: dict[str, Any] = {}


class ExperimentCreate(BaseModel):
    name: str
    description: str
    objective: str
    max_agents: int = 5000


class SwarmCreate(BaseModel):
    swarm_size: int
    algorithm: str = "evolutionary"
    mutation_rate: float = 0.12
    agent_model: str


class AgentResult(BaseModel):
    metrics: dict[str, float]
    runtime_seconds: float


class LeaderboardEntry(BaseModel):
    agent_id: str
    score: float
    parameters: dict[str, Any]
