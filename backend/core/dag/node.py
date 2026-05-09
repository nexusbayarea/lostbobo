from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class DAGNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    node_type: str  # "ingest", "transform", "forecast", "mutate", ...
    compute_fn: Callable[[dict[str, Any]], Any] | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0"
    metadata: dict[str, Any] = Field(default_factory=dict)

    async def execute(self, context: dict[str, Any]) -> Any:
        if self.compute_fn:
            return await self.compute_fn(context)
        return None
