from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class WorldEvent(BaseModel):
    event_id: str
    event_type: str
    tenant_id: str
    plugin_name: str
    timestamp: float
    payload: dict[str, Any]
    vector_clock: dict[str, int]
