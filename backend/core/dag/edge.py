from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class DAGEdge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source: str
    target: str
    weight: float = 1.0  # causal strength / probability flow
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)
