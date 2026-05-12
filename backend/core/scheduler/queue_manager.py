from __future__ import annotations

import asyncio


class QueueManager:
    def __init__(self):
        self.critical = asyncio.PriorityQueue()
        self.high = asyncio.PriorityQueue()
        self.normal = asyncio.PriorityQueue()
        self.low = asyncio.PriorityQueue()

    async def enqueue(self, priority: str, workload):
        queue = getattr(self, priority)
        await queue.put(workload)

    async def dequeue(self):
        for queue_name in ["critical", "high", "normal", "low"]:
            queue = getattr(self, queue_name)
            if not queue.empty():
                return await queue.get()
        return None
