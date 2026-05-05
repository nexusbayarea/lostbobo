"""Claim Extraction Service — turns LLM output into structured claims."""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

log = logging.getLogger(__name__)


class Claim(BaseModel):
    id: str
    type: str  # thermal, mechanical, electrochemical, etc.
    parameters: dict[str, Any]
    confidence: float = Field(ge=0.0, le=1.0)
    source_text: str
    evidence_ids: list[str] = Field(default_factory=list)


class ClaimExtractor:
    async def extract(self, llm_output: str, context: list[dict]) -> list[Claim]:
        """Parse LLM response into structured claims."""
        # In production: use structured LLM output (JSON mode) or Pydantic + LLM
        try:
            # Stub for now — replace with real LLM call
            claims = [
                Claim(
                    id="claim_001",
                    type="thermal",
                    parameters={"max_temperature": 335.0, "c_rate": 3.0},
                    confidence=0.78,
                    source_text=llm_output[:200],
                    evidence_ids=[c.get("id") for c in context[:3]],
                )
            ]
            return claims
        except Exception as e:
            log.error("Claim extraction failed: %s", e)
            return []
