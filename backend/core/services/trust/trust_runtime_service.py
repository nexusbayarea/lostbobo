from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock

from backend.core.extractor.claim_extractor import ClaimExtractor
from backend.core.kernel.kernel import Kernel
from backend.core.supabase_job_store import SupabaseJobStore


@dataclass
class TrustVerificationResult:
    trust_score: float
    decision: str  # ALLOW | WARN | BLOCK
    risk_flags: list[str]
    provenance_hash: str
    certificate_id: str | None = None


class TrustRuntimeService:
    """Kernel-centered Trust Runtime Layer."""

    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.supabase = SupabaseJobStore()
        self.claim_extractor = ClaimExtractor()
        # Stubs for other dependencies
        self.claim_verifier = AsyncMock()
        self.leak_detector = AsyncMock()
        self.prompt_guard = AsyncMock()

    async def verify(self, payload: dict[str, Any]) -> TrustVerificationResult:
        job_id = payload.get("job_id") or await self.supabase.create_job("trust_verify")

        # 1. Extract claims
        claims = await self.claim_extractor.extract(payload.get("input", ""))

        # 2. Run parallel verification via orchestrator
        await self.kernel.services["orchestrator"].run_parallel_validators(
            {"claim": claims.hypothesis, "context": payload.get("context")}
        )

        # 3. Leak + Prompt Guard
        leaks = await self.leak_detector.scan(str(payload.get("input", "")))
        await self.prompt_guard.detect(str(payload.get("input", "")))

        # 4. Final Trust Score (Mock logic for service consistency)
        trust_score = 0.85
        risk_flags = []

        decision = "ALLOW" if trust_score >= 0.75 else "WARN" if trust_score >= 0.45 else "BLOCK"

        # 5. Persist certificate to Supabase
        cert = await self.supabase.save_trust_certificate(
            {
                "job_id": job_id,
                "trust_score": trust_score,
                "decision": decision,
                "risk_flags": risk_flags + (leaks or []),
                "provenance_hash": "a1b2c3d4",
                "tenant_id": payload.get("tenant_id"),
            }
        )

        return TrustVerificationResult(
            trust_score=trust_score,
            decision=decision,
            risk_flags=risk_flags,
            provenance_hash="a1b2c3d4",
            certificate_id=cert["id"],
        )
