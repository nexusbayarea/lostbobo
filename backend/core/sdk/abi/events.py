from __future__ import annotations
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class Event(BaseModel):
    event_type: str
    source: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None
    tenant_id: str = "system"


class EventFilter(BaseModel):
    event_type: Optional[str] = None
    source: Optional[str] = None
    correlation_id: Optional[str] = None


class EventDeliveryGuarantee(str, Enum):
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"
