"""Certificate Service — issues verifiable trust certificates."""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from typing import Any

from backend.app.core.supabase import get_supabase_client
from backend.core.models.hypothesis import Hypothesis

log = logging.getLogger(__name__)


@dataclass
class Certificate:
    certificate_id: str
    hypothesis_id: str
    trust_score: float
    stage: str
    issued_at: float
    data: dict[str, Any]


class CertificateService:
    """Issues cryptographically verifiable certificates for completed hypotheses."""

    async def issue(self, h: Hypothesis) -> Certificate:
        sb = get_supabase_client()
        if not sb:
            log.warning("Supabase unavailable — certificate skipped")
            return None

        payload = {
            "hypothesis_id": h.id,
            "trust_score": h.trust_score,
            "claim": h.claim,
            "sim_params": h.sim_params,
            "sim_result": h.sim_result,
            "stage": h.stage,
        }
        cert_id = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]

        cert = Certificate(
            certificate_id=cert_id,
            hypothesis_id=h.id,
            trust_score=h.trust_score,
            stage=h.stage,
            issued_at=time.time(),
            data=payload,
        )

        try:
            sb.table("certificates").insert(
                {
                    "certificate_id": cert_id,
                    "hypothesis_id": h.id,
                    "trust_score": h.trust_score,
                    "stage": h.stage,
                    "data": payload,
                    "created_at": "now()",
                }
            ).execute()
            log.info("Certificate issued: %s (trust: %.3f)", cert_id, h.trust_score)
        except Exception as e:
            log.error("Failed to issue certificate: %s", e)

        return cert
