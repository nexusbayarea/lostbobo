"""Memory API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.core.memory.schema import MemoryRecord
from backend.core.memory.service import MemoryService

router = APIRouter(prefix="/memory", tags=["memory"])
service = MemoryService()


@router.post("/record")
async def record_memory(record: dict[str, Any]) -> dict[str, Any]:
    mem = MemoryRecord(**record)
    result = await service.record(mem)
    return {"id": result.id, "type": result.type}


@router.post("/query")
async def query_memory(filter: dict[str, Any], limit: int = 50) -> list[dict[str, Any]]:
    results = await service.query(filter, limit)
    return [{"id": r.id, "type": r.type} for r in results]


@router.post("/reconcile/{memory_id}")
async def reconcile(memory_id: str, observed: dict[str, Any]) -> dict[str, Any]:
    result = await service.reconcile(memory_id, observed)
    if result:
        return {"id": result.id, "error": result.outcome.get("error")}
    return {"error": "not found"}
