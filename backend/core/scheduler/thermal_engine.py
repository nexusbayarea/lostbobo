from __future__ import annotations

from backend.core.scheduler.resource_graph import ResourceNode


class ThermalEngine:
    def select_best(
        self, candidates: list[tuple[str, ResourceNode]], workload
    ) -> tuple[str, ResourceNode, float] | None:
        scored = []
        for node_id, node in candidates:
            temp = node.metadata.get("temperature", 60)  # lower is cooler
            scored.append((node_id, node, temp))
        scored.sort(key=lambda x: x[2])
        if scored:
            return scored[0]
        return None
