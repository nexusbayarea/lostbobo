"""Simulation Swarm API Routes."""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter

from backend.runtime.swarm.models import (
    AgentResult,
    ExperimentCreate,
    SwarmCreate,
)
from backend.runtime.swarm.swarm_coordinator import SwarmCoordinator

router = APIRouter(prefix="/api/v1", tags=["swarm"])

coordinator = SwarmCoordinator()


@router.post("/experiments")
async def create_experiment(exp: ExperimentCreate):
    experiment_id = f"exp_{int(time.time() * 1000)}"
    await coordinator.create_experiment(experiment_id, exp.model_dump())
    return {"experimentId": experiment_id, "status": "created"}


@router.post("/experiments/{experiment_id}/swarms")
async def launch_swarm(experiment_id: str, swarm: SwarmCreate):
    swarm_id = f"swarm_{int(time.time() * 1000)}"
    await coordinator.launch_swarm(experiment_id, swarm_id, swarm.model_dump())
    return {"swarmId": swarm_id, "status": "running"}


@router.post("/agents/run")
async def run_agent(payload: dict[str, Any]):
    await coordinator.run_single_agent(payload)
    return {"status": "running", "agent_id": payload.get("agentId")}


@router.post("/agents/{agent_id}/results")
async def submit_results(agent_id: str, result: AgentResult):
    await coordinator.submit_agent_result(agent_id, result.model_dump())
    return {"status": "received"}


@router.get("/swarms/{swarm_id}/leaderboard")
async def get_leaderboard(swarm_id: str):
    return await coordinator.get_leaderboard(swarm_id)


@router.post("/swarms/{swarm_id}/terminate")
async def terminate_swarm(swarm_id: str):
    await coordinator.terminate_swarm(swarm_id)
    return {"status": "terminated"}
