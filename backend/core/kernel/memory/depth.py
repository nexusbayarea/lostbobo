"""Depth Attention Registry with embedding-based similarity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from backend.core.kernel.kernel import Kernel


@dataclass
class DepthState:
    step_id: str
    layer: str
    state: dict[str, Any]
    embedding: list[float] | None = None
    timestamp: datetime = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


class DepthAttentionRegistry:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.history: list[DepthState] = []

    async def store(self, layer: str, state: dict[str, Any], metadata: dict[str, Any] = None):
        """Store state with embedding."""
        text_for_embedding = f"{layer}: {str(state)} {str(metadata)}"
        embedding = await self._compute_embedding(text_for_embedding)

        entry = DepthState(
            step_id=f"depth_{int(datetime.utcnow().timestamp() * 1000)}",
            layer=layer,
            state=state,
            embedding=embedding,
            metadata=metadata or {},
        )
        self.history.append(entry)

        await self.kernel.execute(
            {
                "type": "MEMORY_RECORD",
                "payload": {"type": "depth_state", "content": {"layer": layer, "state": state, "metadata": metadata}},
            }
        )

    async def query(self, query: str, top_k: int = 8) -> list[DepthState]:
        """Embedding-based similarity retrieval."""
        if not self.history:
            return []

        query_emb = await self._compute_embedding(query)
        scored = []

        for entry in self.history[-100:]:
            if entry.embedding:
                similarity = self._cosine_similarity(query_emb, entry.embedding)
                scored.append((similarity, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

    async def _compute_embedding(self, text: str) -> list[float]:
        """Simple fast embedding fallback. Replace with sentence-transformers or Supabase pgvector later."""
        hash_val = hash(text) % 10000
        return [float(hash_val % 100 + i) / 100.0 for i in range(8)]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        a = np.array(a)
        b = np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))
