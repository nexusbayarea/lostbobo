from fastapi import APIRouter

from backend.core.runtime.entity_graph.query import AdvancedGraphQueryEngine, GraphQuery

router = APIRouter(prefix="/graph", tags=["Advanced Graph Query"])


@router.post("/query")
async def advanced_graph_query(query: GraphQuery):
    """Execute any advanced graph query (start node, filters, depth, etc.)."""
    return await AdvancedGraphQueryEngine.query().execute(query)


@router.get("/paths/{source_id}/{target_id}")
async def find_causal_paths(source_id: str, target_id: str, max_hops: int = 6):
    """Find all causal paths between two entities."""
    return await AdvancedGraphQueryEngine.query().find_causal_paths(source_id, target_id, max_hops)


@router.get("/influence/{entity_id}")
async def get_influence(entity_id: str, top_k: int = 20):
    """Get influence ranking for an entity."""
    return await AdvancedGraphQueryEngine.query().rank_influence(entity_id, top_k)


@router.get("/provenance/{run_id}")
async def get_provenance_trace(run_id: str, depth: int = 5):
    """Convenience endpoint for full execution provenance trace."""
    from backend.core.runtime.provenance.service import ExecutionProvenanceService

    return await ExecutionProvenanceService.provenance().get_provenance_trace(run_id, depth)
