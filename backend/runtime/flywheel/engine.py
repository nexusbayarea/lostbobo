from typing import Any


class FlywheelEngine:
    """Welford-based online statistics for aggregation."""

    def __init__(self):
        self.stats: dict[str, dict[str, float]] = {}

    def update(self, domain: str, solver: str, values: dict[str, float]):
        key = f"{domain}:{solver}"
        if key not in self.stats:
            self.stats[key] = {"count": 0, "mean": {k: 0.0 for k in values}, "m2": {k: 0.0 for k in values}}

        s = self.stats[key]
        s["count"] += 1
        for k, v in values.items():
            delta = v - s["mean"][k]
            s["mean"][k] += delta / s["count"]
            delta2 = v - s["mean"][k]
            s["m2"][k] += delta * delta2

    def get_prior(self, domain: str, solver: str) -> dict[str, Any]:
        key = f"{domain}:{solver}"
        if key not in self.stats:
            return {}
        s = self.stats[key]
        return {
            "mean": s["mean"],
            "variance": s["m2"] / (s["count"] - 1) if s["count"] > 1 else {k: 0.0 for k in s["mean"]},
        }
