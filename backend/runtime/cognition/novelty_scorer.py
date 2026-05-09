from datetime import datetime
from typing import Any

import numpy as np
import structlog

from backend.core.kernel.kernel import Kernel
from backend.core.supabase_job_store import SupabaseJobStore

log = structlog.get_logger(__name__)


class NoveltyScorer:
    """Advanced multi-dimensional entropy and novelty monitoring."""

    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.supabase = SupabaseJobStore()

    async def compute(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Returns comprehensive novelty + entropy report."""
        job_id = payload.get("job_id")
        agent_results = payload.get("agent_results", {})
        fused_context = payload.get("fused_context", {})
        is_reflection = payload.get("is_reflection_step", False)

        scores = {}

        # 1. Semantic Entropy (embedding diversity)
        current_text = str(agent_results) + str(fused_context)
        current_emb = await self.kernel.services["embedding"].embed(current_text)
        recent_embs = await self.supabase.get_previous_cognition_embeddings(job_id, limit=15)

        if recent_embs:
            similarities = [np.dot(current_emb, prev) for prev in recent_embs]
            semantic_novelty = 1.0 - np.mean(similarities)
            semantic_entropy = -np.mean([p * np.log(p + 1e-9) for p in similarities])
        else:
            semantic_novelty = 1.0
            semantic_entropy = 1.0

        scores["semantic_novelty"] = round(float(semantic_novelty), 4)
        scores["semantic_entropy"] = round(float(semantic_entropy), 4)

        # 2. Structural Entropy
        graph_stats = await self.kernel.services["execution_graph"].get_stats(job_id)
        total_nodes = graph_stats.get("total_nodes", 1)
        new_nodes = graph_stats.get("new_nodes", 0)
        structural_novelty = min(1.0, new_nodes / total_nodes)

        scores["structural_novelty"] = round(float(structural_novelty), 4)

        # 3. Temporal Entropy
        temporal_novelty = await self._compute_temporal_novelty(job_id)
        scores["temporal_novelty"] = round(float(temporal_novelty), 4)

        # 4. Confidence Entropy
        trust_scores = [r.get("trust_score", 0.5) for r in agent_results.values()]
        confidence_entropy = np.var(trust_scores) if trust_scores else 0.0
        scores["confidence_entropy"] = round(float(confidence_entropy), 4)

        # 5. Reflection Spiral Penalty
        reflection_penalty = 0.35 if is_reflection and semantic_novelty < 0.3 else 0.0

        novelty_score = (
            semantic_novelty * 0.35
            + structural_novelty * 0.25
            + temporal_novelty * 0.20
            + (1.0 - confidence_entropy) * 0.20
            - reflection_penalty
        )
        novelty_score = max(0.0, min(1.0, float(novelty_score)))

        scores["composite_novelty"] = round(float(novelty_score), 4)
        scores["overall_risk"] = "HIGH" if novelty_score < 0.35 else "MEDIUM" if novelty_score < 0.6 else "LOW"

        # Persist to Supabase
        await self.supabase.record_event(
            "novelty_scored", {"job_id": job_id, **scores, "timestamp": datetime.now().isoformat()}
        )

        return scores

    async def _compute_temporal_novelty(self, job_id: str) -> float:
        """Measures rate of change in recent cognition nodes."""
        history = await self.supabase.get_execution_history(job_id, limit=30)
        if len(history) < 5:
            return 1.0
        recent_ops = [n.get("operation") for n in history[-15:]]
        unique_ops = len(set(recent_ops))
        return min(1.0, float(unique_ops / 8.0))
