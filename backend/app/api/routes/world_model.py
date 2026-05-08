from fastapi import APIRouter, Query

from backend.core.kernel.command_bus import command_bus

router = APIRouter(prefix="/world_model", tags=["world_model"])


@router.get("/{job_id}/temporal-history")
async def get_temporal_history(
    job_id: str,
    limit: int = Query(100, le=500),
    start_time: str | None = None,
    end_time: str | None = None,
):
    """Full temporal history with Monte-Carlo samples."""
    return await command_bus.execute(
        "WORLD_TEMPORAL_HISTORY", {"job_id": job_id, "limit": limit, "start_time": start_time, "end_time": end_time}
    )


@router.get("/{job_id}/monte-carlo-samples")
async def get_monte_carlo_samples(
    job_id: str,
    entity: str | None = None,
    limit_samples: int = Query(100, le=500),
):
    """Monte-Carlo distribution samples for a specific entity or all entities."""
    return await command_bus.execute(
        "WORLD_MC_SAMPLES", {"job_id": job_id, "entity": entity, "limit_samples": limit_samples}
    )


@router.get("/{job_id}/uncertainty-evolution")
async def get_uncertainty_evolution(job_id: str, entity: str | None = None):
    """Uncertainty trends over time (mean + std) for Grafana."""
    return await command_bus.execute("WORLD_UNCERTAINTY_EVOLUTION", {"job_id": job_id, "entity": entity})


@router.get("/{job_id}/novelty-trends")
async def get_novelty_trends(job_id: str):
    """Novelty + entropy trends correlated with world states."""
    return await command_bus.execute("WORLD_NOVELTY_TRENDS", {"job_id": job_id})


@router.get("/{job_id}/state-comparison")
async def compare_states(job_id: str, state_id1: str, state_id2: str):
    """Compare two temporal states (diff + uncertainty delta)."""
    return await command_bus.execute(
        "WORLD_STATE_COMPARISON", {"job_id": job_id, "state_id1": state_id1, "state_id2": state_id2}
    )


@router.get("/active-jobs")
async def get_active_world_states():
    """List currently evolving world states across tenants."""
    return await command_bus.execute("WORLD_ACTIVE_STATES", {})
