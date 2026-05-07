import asyncio
import logging

import redis.asyncio as redis

from backend.core.kernel.kernel import get_kernel

log = logging.getLogger(__name__)


class SimulationPriorityWorker:
    """Background worker that drains priority queues to A40"""

    def __init__(self):
        self.redis = redis.from_url("redis://localhost:6379")
        self.running = True

    async def run(self):
        """Main worker loop"""
        while self.running:
            try:
                # Check priorities: critical > premium > normal > background
                for priority in ["critical", "premium", "normal", "background"]:
                    queue_key = f"sim:queue:priority:{priority}"
                    hyp_id = await self.redis.rpop(queue_key)
                    if hyp_id:
                        log.info(f"Dequeuing simulation {hyp_id} (priority={priority})")
                        await self._launch_simulation(hyp_id)
                        break  # one at a time to respect concurrency limit
                await asyncio.sleep(0.5)
            except Exception as e:
                log.error(f"Simulation worker error: {e}")
                await asyncio.sleep(1)

    async def _launch_simulation(self, hypothesis_id: str):
        """Send to SimHPC / A40"""
        await get_kernel().execute(
            {"type": "WORLD_SIMULATE", "payload": {"hypothesis_id": hypothesis_id, "source": "priority_worker"}}
        )

    async def stop(self):
        self.running = False


# Global worker
_simulation_worker: SimulationPriorityWorker | None = None


async def start_simulation_worker():
    global _simulation_worker
    if _simulation_worker is None:
        _simulation_worker = SimulationPriorityWorker()
        asyncio.create_task(_simulation_worker.run())
