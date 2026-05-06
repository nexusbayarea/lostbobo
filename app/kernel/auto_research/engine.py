"""Auto-Research Engine — closed-loop optimization (Kernel-managed)."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, Any

from app.kernel.auto_research.memory import ResearchMemory, ExperimentRecord
from app.kernel.auto_research.evaluation import compute_score, run_simulation_gate
from app.kernel.kernel import Kernel

log = logging.getLogger(__name__)


class AutoResearchEngine:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.memory = ResearchMemory(kernel)

    async def run_research_cycle(
        self, target: str, research_dsl: Dict[str, Any]
    ) -> Dict[str, Any]:
        """One full auto-research iteration."""
        experiment_id = f"exp_{int(datetime.utcnow().timestamp() * 1000)}"

        # 1. Propose change (limited search space)
        proposed_change = await self._propose_change(research_dsl)

        # 2. Run experiment (time-boxed via Kernel)
        experiment_result = await self.kernel.execute(
            {
                "type": "SKILL_EXECUTE",
                "payload": {
                    "skill": research_dsl.get("skill"),
                    "input": proposed_change,
                },
            }
        )

        # 3. Evaluate (multi-objective + uncertainty)
        score = compute_score(experiment_result)
        accepted = run_simulation_gate(experiment_result) and score > research_dsl.get(
            "baseline_score", 0
        )

        # 4. Log to Research Memory
        record = ExperimentRecord(
            id=experiment_id,
            timestamp=datetime.utcnow(),
            target=target,
            change=proposed_change,
            result={**experiment_result, "score": score},
            accepted=accepted,
            experiment_id=experiment_id,
        )
        await self.memory.log(record)

        log.info(
            f"Auto-research cycle complete → {target} | score={score:.3f} | accepted={accepted}"
        )

        return {
            "experiment_id": experiment_id,
            "accepted": accepted,
            "score": score,
            "change": proposed_change,
            "result": experiment_result,
        }

    async def _propose_change(self, research_dsl: Dict[str, Any]) -> Dict[str, Any]:
        """Controlled mutation within DSL-defined search space."""
        # Example search space from DSL
        return {
            "parameter": "batch_size",
            "value": 64,  # sampled from DSL constraints
            "reason": "auto-research proposal",
        }
