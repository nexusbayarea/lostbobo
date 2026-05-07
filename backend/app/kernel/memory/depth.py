"""Depth Attention Registry — queryable history of computation states."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.kernel.kernel import Kernel


@dataclass
class DepthState:
    step_id: str
    layer: str
    state: dict[str, Any]
    embedding: list[float] | None = None
    timestamp: datetime = None

    def __post_init__(self):
        if not self.step_id:
            self.step_id = f"step_{int(datetime.utcnow().timestamp() * 1000)}"
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


class DepthAttentionRegistry:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.history: list[DepthState] = []

    async def store(self, layer: str, state: dict[str, Any]):
        entry = DepthState(
            step_id=f"step_{int(datetime.utcnow().timestamp() * 1000)}",
            layer=layer,
            state=state,
            timestamp=datetime.utcnow()
        )
        self.history.append(entry)

        await self.kernel.execute({
            "type": "MEMORY_RECORD",
            "payload": {
                "type": "depth_state",
                "content": {"layer": layer, **state}
            }
        })

    async def query(self, query_text: str, top_k: int = 5) -> list[DepthState]:
        # For now: last N + keyword match
        return self.history[-top_k:]
