from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.app.core.supabase import get_supabase_client


@dataclass
class BenchmarkTask:
    task_name: str
    examples_count: int
    accuracy: float
    latency_ms: float
    tokens_per_second: float
    improvement_vs_base: float
    notes: str = ""


@dataclass
class ModelBenchmark:
    model_id: str
    version: str
    base_model: str
    created_at: str
    trained_on_runs: int
    training_domains: list[str]
    benchmark_date: str
    hypothesis_verification: BenchmarkTask
    parameter_prediction: BenchmarkTask
    uncertainty_quantification: BenchmarkTask
    sensitivity_analysis: BenchmarkTask
    mean_accuracy: float
    mean_latency_ms: float
    mean_improvement_vs_base: float
    model_size_mb: float
    inference_memory_mb: float
    inference_throughput: int

    def get_overall_score(self) -> float:
        return (
            0.5 * self.mean_accuracy
            + 0.3 * (1.0 - min(self.mean_latency_ms / 1000, 1.0))
            + 0.2 * min(self.mean_improvement_vs_base / 50, 1.0)
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ModelRegistry:
    def __init__(self, registry_dir: str = "./simhpc_model_registry"):
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self._db = get_supabase_client()
        self._models: list[ModelBenchmark] = []

    async def register_model(self, benchmark: ModelBenchmark) -> dict[str, Any]:
        model_dir = self.registry_dir / benchmark.model_id
        model_dir.mkdir(parents=True, exist_ok=True)

        with open(model_dir / "benchmark.json", "w") as f:
            json.dump(benchmark.to_dict(), f, indent=2)

        if self._db:
            self._db.table("model_registry").insert(
                {
                    "model_id": benchmark.model_id,
                    "version": benchmark.version,
                    "created_at": benchmark.created_at,
                    "benchmark_data": benchmark.to_dict(),
                    "overall_score": benchmark.get_overall_score(),
                    "trained_on_runs": benchmark.trained_on_runs,
                }
            ).execute()

        self._models.append(benchmark)

        return {
            "status": "REGISTERED",
            "model_id": benchmark.model_id,
            "overall_score": benchmark.get_overall_score(),
            "mean_accuracy": benchmark.mean_accuracy,
        }

    async def get_latest_model(self) -> ModelBenchmark | None:
        if not self._models:
            await self._load_registry()

        if not self._models:
            return None

        self._models.sort(key=lambda m: m.get_overall_score(), reverse=True)
        return self._models[0]

    async def get_model_by_version(self, version: str) -> ModelBenchmark | None:
        if not self._models:
            await self._load_registry()
        return next((m for m in self._models if m.version == version), None)

    async def compare_models(self, model_a_version: str, model_b_version: str) -> dict[str, Any]:
        a = await self.get_model_by_version(model_a_version)
        b = await self.get_model_by_version(model_b_version)

        if not a or not b:
            return {"status": "ERROR", "reason": "Model not found"}

        return {
            "model_a": {
                "version": a.version,
                "mean_accuracy": a.mean_accuracy,
                "mean_latency_ms": a.mean_latency_ms,
                "overall_score": a.get_overall_score(),
            },
            "model_b": {
                "version": b.version,
                "mean_accuracy": b.mean_accuracy,
                "mean_latency_ms": b.mean_latency_ms,
                "overall_score": b.get_overall_score(),
            },
            "accuracy_difference": round(a.mean_accuracy - b.mean_accuracy, 4),
            "latency_difference_ms": round(a.mean_latency_ms - b.mean_latency_ms, 2),
            "winner": "A"
            if a.get_overall_score() > b.get_overall_score()
            else ("B" if b.get_overall_score() > a.get_overall_score() else "TIE"),
        }

    async def get_performance_trend(self) -> list[dict[str, Any]]:
        if not self._models:
            await self._load_registry()

        models_by_date = sorted(self._models, key=lambda m: m.created_at)

        return [
            {
                "version": m.version,
                "date": m.created_at,
                "trained_on_runs": m.trained_on_runs,
                "mean_accuracy": round(m.mean_accuracy, 4),
                "mean_improvement_vs_base": round(m.mean_improvement_vs_base, 2),
                "overall_score": round(m.get_overall_score(), 4),
            }
            for m in models_by_date
        ]

    async def _load_registry(self) -> None:
        for model_dir in self.registry_dir.glob("*"):
            bench_file = model_dir / "benchmark.json"
            if bench_file.exists():
                with open(bench_file) as f:
                    self._models.append(json.load(f))

        if self._db:
            result = (
                self._db.table("model_registry")
                .select("benchmark_data")
                .order("created_at", desc=True)
                .limit(100)
                .execute()
            )
            if result.data:
                for row in result.data:
                    if "benchmark_data" in row:
                        self._models.append(row["benchmark_data"])


def create_mock_benchmark(version: str, trained_on_runs: int) -> ModelBenchmark:
    base_accuracy = 0.60
    improvement_factor = min(1.0, trained_on_runs / 10000)
    accuracy_boost = 0.25 * improvement_factor

    return ModelBenchmark(
        model_id=f"simhpc-physics-{version}",
        version=version,
        base_model="phi-3-mini",
        created_at=datetime.now(UTC).isoformat(),
        trained_on_runs=trained_on_runs,
        training_domains=["structural", "thermal", "ev_battery"],
        benchmark_date=datetime.now(UTC).isoformat(),
        hypothesis_verification=BenchmarkTask(
            task_name="Hypothesis Verification",
            examples_count=500,
            accuracy=min(0.95, base_accuracy + accuracy_boost + 0.12),
            latency_ms=245,
            tokens_per_second=180,
            improvement_vs_base=15.0 + (trained_on_runs / 1000),
        ),
        parameter_prediction=BenchmarkTask(
            task_name="Parameter Prediction",
            examples_count=400,
            accuracy=min(0.92, base_accuracy + accuracy_boost + 0.10),
            latency_ms=320,
            tokens_per_second=160,
            improvement_vs_base=18.0 + (trained_on_runs / 500),
        ),
        uncertainty_quantification=BenchmarkTask(
            task_name="Uncertainty Quantification",
            examples_count=300,
            accuracy=min(0.88, base_accuracy + accuracy_boost + 0.08),
            latency_ms=280,
            tokens_per_second=170,
            improvement_vs_base=8.0 + (trained_on_runs / 2000),
        ),
        sensitivity_analysis=BenchmarkTask(
            task_name="Sensitivity Analysis",
            examples_count=350,
            accuracy=min(0.91, base_accuracy + accuracy_boost + 0.09),
            latency_ms=290,
            tokens_per_second=165,
            improvement_vs_base=15.0 + (trained_on_runs / 1000),
        ),
        mean_accuracy=round((0.70 + 0.75 + 0.68 + 0.72 + accuracy_boost * 4) / 4, 4),
        mean_latency_ms=283.75,
        mean_improvement_vs_base=round(14 + (trained_on_runs / 1000), 2),
        model_size_mb=3800,
        inference_memory_mb=6400,
        inference_throughput=12,
    )


async def get_model_status() -> dict[str, Any]:
    registry = ModelRegistry()
    latest = await registry.get_latest_model()
    trend = await registry.get_performance_trend()

    if not latest:
        return {
            "status": "NO_MODELS",
            "message": "No fine-tuned models yet. Run training pipeline.",
        }

    return {
        "status": "ACTIVE",
        "latest_model": {
            "version": latest.version,
            "created_at": latest.created_at,
            "trained_on_runs": latest.trained_on_runs,
            "mean_accuracy": latest.mean_accuracy,
            "overall_score": round(latest.get_overall_score(), 4),
        },
        "performance_trend": trend[-5:],
        "moat_strength": (
            "STRONG" if latest.trained_on_runs >= 5000 else "GROWING" if latest.trained_on_runs >= 1000 else "BUILDING"
        ),
        "next_training_recommended_at": latest.trained_on_runs + 1000,
    }
