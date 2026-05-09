from dataclasses import dataclass
from typing import Any

import numpy as np
import structlog

from backend.core.kernel.kernel import Kernel
from backend.core.supabase_job_store import SupabaseJobStore

log = structlog.get_logger(__name__)


@dataclass
class TrustScoreBreakdown:
    overall: float  # 0.0 - 1.0
    grounding: float
    consistency: float
    simulation: float
    robustness: float
    provenance: float
    novelty: float
    risk_penalty: float
    verification_signature_valid: bool


class TrustScoringEngine:
    """Multi-factor trust scoring — Kernel-centered."""

    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.supabase = SupabaseJobStore()

    async def compute(self, payload: dict[str, Any]) -> TrustScoreBreakdown:
        job_id = payload.get("job_id")

        # Gather signals
        cascaded_stages = payload.get("cascaded_stages", [])
        physics_result = payload.get("physics_result", {})
        rag_evidence = payload.get("rag_evidence", [])
        novelty_score = payload.get("novelty_score", 0.5)
        safety_result = payload.get("safety_result", {})

        # Individual Component Scores
        grounding = self._compute_grounding_score(rag_evidence)
        consistency = self._compute_consistency_score(cascaded_stages)
        simulation = self._compute_simulation_score(physics_result)
        robustness = self._compute_robustness_score(physics_result)
        provenance = self._compute_provenance_score(payload)
        novelty = float(novelty_score)

        # Risk penalties
        risk_penalty = 0.0
        if not safety_result.get("safe", True):
            risk_penalty -= 0.4
        if len([s for s in cascaded_stages if not s.get("passed", False)]) > 2:
            risk_penalty -= 0.3

        # Weighted combination
        weights = {
            "grounding": 0.18,
            "consistency": 0.20,
            "simulation": 0.22,
            "robustness": 0.15,
            "provenance": 0.15,
            "novelty": 0.10,
        }

        overall = (
            grounding * weights["grounding"]
            + consistency * weights["consistency"]
            + simulation * weights["simulation"]
            + robustness * weights["robustness"]
            + provenance * weights["provenance"]
            + novelty * weights["novelty"]
        ) + risk_penalty

        overall = float(np.clip(overall, 0.0, 1.0))

        breakdown = TrustScoreBreakdown(
            overall=overall,
            grounding=grounding,
            consistency=consistency,
            simulation=simulation,
            robustness=robustness,
            provenance=provenance,
            novelty=novelty,
            risk_penalty=float(risk_penalty),
            verification_signature_valid=payload.get("verification_signature") is not None,
        )

        # Persist to Supabase
        await self.supabase.save_trust_certificate(
            {
                "job_id": job_id,
                "trust_score": overall,
                "breakdown": breakdown.__dict__,
                "verification_signature": payload.get("verification_signature"),
                "tenant_id": payload.get("tenant_id"),
            }
        )

        return breakdown

    def _compute_grounding_score(self, evidence: list[dict[str, Any]]) -> float:
        if not evidence:
            return 0.0
        scores = [e.get("similarity", 0.0) for e in evidence]
        return float(np.mean(scores)) * (len(scores) / 8.0)

    def _compute_consistency_score(self, stages: list[dict[str, Any]]) -> float:
        passed = sum(1 for s in stages if s.get("passed", False))
        return float(passed / max(len(stages), 1))

    def _compute_simulation_score(self, physics: dict[str, Any]) -> float:
        return float(physics.get("validation_passed", False)) * 0.9 + physics.get("confidence", 0.0) * 0.1

    def _compute_robustness_score(self, physics: dict[str, Any]) -> float:
        return float(physics.get("robustness_score", 0.0))

    def _compute_provenance_score(self, payload: dict[str, Any]) -> float:
        graph_depth = payload.get("execution_graph_depth", 0)
        has_signature = bool(payload.get("verification_signature"))
        return float(min(1.0, (graph_depth / 12.0) * 0.6 + (1.0 if has_signature else 0.0) * 0.4))
