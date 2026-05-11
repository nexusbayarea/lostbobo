"""
backend/core/evaluation/ab_test.py
──────────────────────────────────
Lightweight A/B testing harness for prompt variants on resolved questions.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from backend.core.runtime.event_fabric.log import EventLogService
from backend.core.runtime.event_fabric.schema import SimHPCEvent

log = logging.getLogger(__name__)


@dataclass
class ABTestResult:
    test_id: str
    question_id: str
    variant: str
    resolved_outcome: int
    predicted_prob: float
    brier_score: float
    evidence_ids: list[str]
    cited_evidence_count: int
    timestamp: float
    metadata: dict[str, Any]


class ABTestHarness:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._active_tests = {}
        return cls._instance

    async def start_test(self, question_id: str) -> str:
        test_id = str(uuid4())
        self._active_tests[test_id] = {"question_id": question_id, "started_at": time.time()}
        return test_id

    async def record_result(self, test_id: str, variant: str, result: ABTestResult):
        if test_id not in self._active_tests:
            return

        await EventLogService().publish(
            SimHPCEvent(
                event_type="evaluation.ab_test.result",
                source_plugin="core.evaluation",
                payload={
                    "test_id": test_id,
                    "variant": variant,
                    "question_id": result.question_id,
                    "brier_score": result.brier_score,
                    "evidence_ids": result.evidence_ids,
                    "cited_count": result.cited_evidence_count,
                    "predicted_prob": result.predicted_prob,
                    "outcome": result.resolved_outcome,
                },
                confidence=1.0,
            )
        )

        del self._active_tests[test_id]
        log.info("A/B test %s recorded for variant %s", test_id, variant)

    async def get_test_stats(self, question_id: str | None = None) -> dict[str, Any]:
        return {}


ab_test_harness = ABTestHarness()
