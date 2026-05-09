from dataclasses import dataclass
from typing import Any

import structlog

from backend.core.supabase_job_store import SupabaseJobStore
from backend.core.kernel.kernel import Kernel

log = structlog.get_logger(__name__)


@dataclass
class ExecutionNode:
    """First-class structured cognition node — preserves intermediate reasoning."""

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

    async def add_node(self, node: ExecutionNode, job_id: str):
        """Persist high-fidelity reasoning checkpoint."""
        await self.supabase.record_event(
            "cognition_node",
            {
                "job_id": job_id,
                "node_id": node.node_id,
                "parent_id": node.parent_id,
                "operation": node.operation,
                "state_hash": node.state_hash,
                "trust_score": node.trust_score,
                "confidence": node.confidence,
                "token_cost": node.token_cost,
                "attention_score": node.attention_score,
                "metadata": node.metadata,
                "timestamp": node.timestamp,
            },
        )
        log.info("cognition node recorded", node_id=node.node_id, operation=node.operation)

    async def attend(self, query: str, job_id: str, top_k: int = 8) -> list[ExecutionNode]:
        """Selective attention-based retrieval of relevant prior cognition states."""
        nodes = await self.supabase.get_execution_history(job_id, limit=150)

        scored = []
        for n in nodes:
            metadata = n.get("metadata", {})
            score = (
                n.get("trust_score", 0.0) * 0.45
                + n.get("confidence", 0.0) * 0.25
                + (1.0 if query.lower() in str(metadata).lower() else 0.0) * 0.3
            )
            scored.append((score, n))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [ExecutionNode(**n) for _, n in scored[:top_k]]
