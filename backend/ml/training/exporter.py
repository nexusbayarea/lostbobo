import logging
from dataclasses import dataclass
from typing import Any

from backend.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)


@dataclass
class QualityThresholds:
    min_confidence: float = 0.8
    min_convergence: bool = True

    @staticmethod
    def production():
        return QualityThresholds()


class TrainingDataExporter:
    def __init__(self, thresholds: QualityThresholds = None):
        self.thresholds = thresholds or QualityThresholds.production()
        self.db = get_supabase_client()

    async def get_dataset_stats(self) -> dict[str, Any]:
        count = self.db.table("simulation_runs").select("*", count="exact").eq("status", "COMPLETED").execute().count
        return {"ready_for_training": (count or 0) >= 1000, "count": count or 0}

    async def export(self, output_dir: str = "./training_data"):
        logger.info(f"🚀 Exporting training data to {output_dir}")
        # Logic to export from simulation_runs to JSONL
