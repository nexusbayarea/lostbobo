"""World Brain — Central Cognitive Substrate."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from backend.core.kernel.memory.depth import DepthAttentionRegistry

if TYPE_CHECKING:
    from backend.core.kernel.kernel import Kernel

log = logging.getLogger(__name__)


class WorldBrain:
    """Single Brain — maintains unified latent world state."""

    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.depth_registry = DepthAttentionRegistry(kernel)

        self.global_state: dict[str, Any] = {}
        self.causal_graph: dict[str, Any] = {}
        self.uncertainty_field: dict[str, float] = {}

        log.info("World Brain initialized — Global Cognitive Kernel active")

    async def update(self, domain: str, update: dict[str, Any]) -> dict[str, Any]:
        """Update global state with causal linking."""
        self.global_state[domain] = update

        await self.depth_registry.store(layer=f"world_brain_{domain}", state=update, metadata={"domain": domain})

        self.uncertainty_field[domain] = update.get("uncertainty", 0.1)

        return self.global_state

    async def query(self, query: str) -> dict[str, Any]:
        """Cross-domain query with depth attention."""
        depth_context = await self.depth_registry.query(query, top_k=10)
        return {
            "global_state": self.global_state,
            "depth_context": [d.state for d in depth_context],
            "uncertainty_summary": self.uncertainty_field,
        }
