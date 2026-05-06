"""MemoryRecord — structured episodic memory for the closed loop."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

MemoryType = Literal["decision", "observation", "outcome", "hypothesis"]


@dataclass
class MemoryRecord:
    id: str
    type: MemoryType
    timestamp: datetime

    context: dict[str, Any]
    content: dict[str, Any]
    outcome: dict[str, Any]
    links: dict[str, list[str]]
    tenant_id: str

    def __post_init__(self):
        if not self.id:
            self.id = f"mem_{int(datetime.now().timestamp()*1000)}"
        if not self.timestamp:
            self.timestamp = datetime.utcnow()
        if not self.context:
            self.context = {}
        if not self.content:
            self.content = {}
        if not self.outcome:
            self.outcome = {}
        if not self.links:
            self.links = {"parent_ids": [], "child_ids": []}
        if not self.tenant_id:
            self.tenant_id = "public"
