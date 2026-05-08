from dataclasses import dataclass
from datetime import datetime
from typing import Any

import structlog

from backend.core.supabase_job_store import SupabaseJobStore
from backend.kernel.kernel import Kernel

log = structlog.get_logger(__name__)


@dataclass
class ExecutionNode:
    """First-class representation of structured intermediate cognition."""

    node_id: str
    parent_id: str | None
    operation: str  # reason, tool_call, verify, reflect, simulate, retrieve...
    state_hash: str
    trust_score: float
    confidence: float
    token_cost: int
    timestamp: str
    metadata: dict[str, Any]
    attention_score: float = 0.0


class ExecutionAttentionGraph:
    """Preserves recoverable cognition states as addressable graph nodes."""

    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.supabase = SupabaseJobStore()

    async def add_node(self, node_data: dict[str, Any], job_id: str):
        """Persist high-fidelity reasoning checkpoint."""
        await self.supabase.record_event(
            "cognition_node", {"job_id": job_id, **node_data, "timestamp": datetime.now().isoformat()}
        )
        log.info("cognition node recorded", node_id=node_data.get("node_id"), operation=node_data.get("operation"))

    async def attend(self, query: str, job_id: str, top_k: int = 8) -> list[dict[str, Any]]:
        """Selective attention-based retrieval of relevant prior cognition states."""
        nodes = await self.supabase.get_execution_history(job_id, limit=200)

        # Score nodes by semantic + trust + temporal relevance
        scored_nodes = []
        for n in nodes:
            metadata = n.get("metadata", {})
            score = (
                n.get("trust_score", 0.0) * 0.5
                + (1.0 if query.lower() in str(metadata).lower() else 0.0) * 0.3
                + n.get("confidence", 0.0) * 0.2
            )
            scored_nodes.append((score, n))

        scored_nodes.sort(key=lambda x: x[0], reverse=True)
        return [n for _, n in scored_nodes[:top_k]]

    async def get_stats(self, job_id: str) -> dict[str, Any]:
        """Return execution graph statistics."""
        history = await self.supabase.get_execution_history(job_id)
        return {
            "history": history,
            "total_nodes": len(history),
            "new_nodes": len([n for n in history if n.get("operation") != "retrieve"]),
        }
