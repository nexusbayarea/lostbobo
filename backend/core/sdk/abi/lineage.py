from __future__ import annotations
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class LineageRecord(BaseModel):
    plugin_name: str
    capability: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    trace_id: str
    parent_trace_id: Optional[str] = None
    deterministic_hash: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LineageQuery(BaseModel):
    trace_id: Optional[str] = None
    plugin_name: Optional[str] = None
    capability: Optional[str] = None
    since: Optional[datetime] = None
    until: Optional[datetime] = None
    limit: int = 100
