from fastapi import APIRouter
from backend.core.middleware.llm_cost_gate import get_llm_cost_gate
from backend.core.middleware.rate_limiter import get_rate_limiter

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/cost/spend/{tenant_id}")
async def get_spend(tenant_id: str):
    gate = get_llm_cost_gate()
    return await gate.get_spend_report(tenant_id)


@router.get("/rate-limits/stats")
async def rate_limit_stats():
    limiter = get_rate_limiter()
    return {"total_hits": 0}
