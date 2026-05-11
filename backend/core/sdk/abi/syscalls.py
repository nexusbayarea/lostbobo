from __future__ import annotations


class KernelSyscalls:
    def __init__(self, kernel):
        self.kernel = kernel

    async def emit_event(self, event: str, payload: dict):
        return await self.kernel.events.emit(event, payload)

    async def allocate_gpu(self, profile: str):
        return await self.kernel.scheduler.allocate_gpu(profile)

    async def write_lineage(self, payload: dict):
        return await self.kernel.lineage.record(payload)

    async def memory_read(self, namespace: str, key: str):
        return await self.kernel.memory.read(namespace, key)

    async def memory_write(self, namespace: str, key: str, value):
        return await self.kernel.memory.write(namespace, key, value)
