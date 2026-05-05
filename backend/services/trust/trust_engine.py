"""Trust Score + Certificate Engine."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from backend.app.core.supabase import get_supabase_client


@dataclass
class TrustScore:
    overall: float
    simulation_agreement: float = 0.0
    robustness: float = 0.0
    rag_similarity: float = 0.0
    consensus: float = 0.0


class TrustEngine:
    def compute(self, verification_results: list[dict]) -> TrustScore:
        """Deterministic trust scoring."""
        # Placeholder weights — tune based on domain
        sim = 0.4
        robust = 0.25
        rag = 0.2
        cons = 0.15

        overall = sim * 0.9 + robust * 0.85 + rag * 0.95 + cons * 0.88

        return TrustScore(overall=round(overall, 4))

    async def issue_certificate(self, result: dict, trust: TrustScore) -> str:
        sb = get_supabase_client()
        cert_id = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()[:16]

        if sb:
            sb.table("certificates").insert(
                {"certificate_id": cert_id, "trust_score": trust.overall, "data": result, "timestamp": "now()"}
            ).execute()

        return cert_id
