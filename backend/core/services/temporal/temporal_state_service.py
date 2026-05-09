from dataclasses import dataclass
from datetime import datetime
from typing import Any

from backend.core.kernel.kernel import Kernel
from backend.core.supabase_job_store import SupabaseJobStore
from backend.core.world_model.schema import Uncertainty, WorldState


@dataclass
class TemporalState:
    """Unified temporal probabilistic state."""

    job_id: str
    timestamp: datetime
    state_hash: str
    world_state: WorldState
    local_cognition: dict[str, Any]
    global_cognition: dict[str, Any]
    uncertainty: Uncertainty
    novelty_score: float
    trust_score: float


class TemporalProbabilisticStateService:
    """Unified temporal + probabilistic state management."""

    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.supabase = SupabaseJobStore()

    async def evolve_state(self, payload: dict[str, Any]) -> TemporalState:
        """Advance the unified temporal state."""
        job_id = payload["job_id"]
        current_time = datetime.utcnow()

        previous = await self.supabase.get_latest_temporal_state(job_id)

        # 1. Update World Model with temporal propagation
        world_update = await self.kernel.services["world_model"].evolve(
            previous.world_state if previous else None, payload.get("new_evidence", {}), payload.get("physics_result")
        )

        # 2. Update cognition graph
        await self.kernel.services["execution_graph"].add_temporal_node(payload, current_time)

        # 3. Compute novelty & uncertainty
        novelty = await self.kernel.services["novelty_scorer"].compute(payload)
        uncertainty = await self.kernel.services["world_model"].propagate_uncertainty(world_update)

        # 4. Build unified temporal state
        state = TemporalState(
            job_id=job_id,
            timestamp=current_time,
            state_hash=await self.kernel.services["state_hasher"].hash(world_update.dict()),
            world_state=world_update,
            local_cognition=await self.kernel.services["multi_res_cognition"].get_local_state(job_id),
            global_cognition=await self.kernel.services["multi_res_cognition"].get_global_state(),
            uncertainty=uncertainty,
            novelty_score=novelty.get("composite_novelty", 0.0),
            trust_score=payload.get("trust_score", 0.85),
        )

        # Persist to Supabase
        await self.supabase.save_temporal_state(
            {
                "job_id": job_id,
                "timestamp": current_time.isoformat(),
                "state_hash": state.state_hash,
                "world_state": state.world_state.dict(),
                "local_cognition": state.local_cognition,
                "global_cognition": state.global_cognition,
                "uncertainty": state.uncertainty.dict(),
                "novelty_score": state.novelty_score,
                "trust_score": state.trust_score,
            }
        )

        return state
