# backend/app/api/lineage.py
from typing import Any

from fastapi import APIRouter
from backend.app.core.supabase import get_supabase_client

router = APIRouter(prefix="/lineage", tags=["Lineage"])


@router.get("/executions")
async def list_executions(limit: int = 50):
    """List recent executions with summary stats."""
    result = (
        await get_supabase_client()
        .table("execution_lineage")
        .select("execution_id, created_at, event_type")
        .order("created_at", desc=True)
        .limit(limit * 10)  # Fetch more to aggregate
        .execute()
    )

    # Group by execution_id and compute summary
    executions: dict[str, Any] = {}
    for row in result.data or []:
        eid = row["execution_id"]
        if eid not in executions:
            executions[eid] = {
                "execution_id": eid,
                "total_events": 0,
                "last_event": row["created_at"],
                "source_types": set(),
            }
        executions[eid]["total_events"] += 1
        executions[eid]["source_types"].add(row["event_type"])

    # Finalize stats
    summary = []
    for _eid, data in executions.items():
        data["source_types"] = list(data["source_types"])
        summary.append(data)

    return summary[:limit]

