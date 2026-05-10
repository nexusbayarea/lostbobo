# backend/app/api/graph_viz.py

from fastapi import APIRouter

from backend.core.kernel.lineage.graph import ProvenanceGraph
from backend.core.runtime.entity_graph.service import EntityGraphService
from backend.core.runtime.provenance.service import ExecutionProvenanceService

router = APIRouter(prefix="/graph", tags=["Visualization"])


@router.get("/provenance/{run_id}")
async def get_provenance_graph(run_id: str, depth: int = 5):
    """Full provenance trace for one execution."""
    return await ExecutionProvenanceService.provenance().get_provenance_trace(run_id, depth)


@router.get("/lineage/{execution_id}")
async def get_lineage_graph(execution_id: str):
    """Dedicated lineage graph for an execution (simpler, event-focused)."""
    graph = await ProvenanceGraph().build(execution_id)
    return graph.to_dict()


@router.get("/world-state")
async def get_world_state_graph():
    return await EntityGraphService.graph().get_world_state_graph()


@router.get("/temporal-snapshot")
async def get_temporal_snapshot(timestamp: str | None = None):
    return await EntityGraphService.graph().get_temporal_snapshot(timestamp)
