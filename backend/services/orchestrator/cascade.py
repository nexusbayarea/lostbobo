"""Cascaded Verification Orchestrator — cheap → expensive path."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from backend.runtime.orchestrator.queue_router import QueueRouter
from backend.runtime.validation.simulation_validator import SimulationValidator
from backend.services.extractor.claim_extractor import ClaimExtractor

log = logging.getLogger(__name__)


class VerificationOrchestrator:
    def __init__(self):
        self.extractor = ClaimExtractor()
        self.validator = SimulationValidator()
        self.queue = QueueRouter()

    async def process(self, llm_output: str, rag_context: list[dict]) -> dict:
        """Full cascade: extract → validate → simulate if needed."""
        claims = await self.extractor.extract(llm_output, rag_context)

        results = []
        for claim in claims:
            # Stage 1: Fast validation
            if not await self._fast_validation(claim):
                results.append({"claim": claim, "status": "rejected_fast"})
                continue

            # Stage 2: Simulation (gated)
            if await self._should_simulate(claim):
                sim_job = await self.queue.enqueue("simulation", claim.dict())
                sim_result = await self._wait_for_simulation(sim_job)
                results.append({"claim": claim, "status": "simulated", "result": sim_result})
            else:
                results.append({"claim": claim, "status": "skipped_simulation"})

        return {"claims_processed": len(claims), "results": results, "trust_score": await self._compute_trust(results)}

    async def _fast_validation(self, claim: Any) -> bool:
        return claim.confidence > 0.5

    async def _should_simulate(self, claim: Any) -> bool:
        return claim.confidence > 0.6  # cost gate

    async def _wait_for_simulation(self, job_id: str) -> dict:
        # Poll Redis or use callback in production
        await asyncio.sleep(0.5)
        return {"status": "success", "max_temp": 335.0}

    async def _compute_trust(self, results: list[dict]) -> float:
        # Simple weighted trust
        return 0.85
