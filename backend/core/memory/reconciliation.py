"""Outcome reconciliation engine — closes the learning loop."""

from __future__ import annotations

from typing import Any

from backend.core.memory.service import MemoryService


async def reconcile_outcome(memory_id: str, observed: dict[str, Any]):
    """Public helper used by agents / external systems."""
    service = MemoryService()
    return await service.reconcile(memory_id, observed)
