"""Swarm Scheduler — allocates compute and manages swarms."""

from __future__ import annotations

import time
from typing import Any

from backend.runtime.swarm.swarm_coordinator import SwarmCoordinator


class SwarmScheduler:
    def __init__(self, kernel: Any = None):
        self.kernel = kernel
        self.coordinators: dict[str, SwarmCoordinator] = {}

    async def allocate_swarm(self, experiment_id: str, swarm_size: int, algorithm: str = "evolutionary") -> str:
        swarm_id = f"swarm_{int(time.time() * 1000)}"
        coordinator = SwarmCoordinator()
        self.coordinators[swarm_id] = coordinator
        return swarm_id
