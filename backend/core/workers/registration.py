from __future__ import annotations

from typing import Any


class WorkerCapabilities:
    def __init__(
        self,
        worker_id: str,
        capabilities: list[str],
        gpu_memory_mb: int = 0,
    ):
        self.worker_id = worker_id
        self.capabilities = capabilities
        self.gpu_memory_mb = gpu_memory_mb

    def to_dict(self) -> dict[str, Any]:
        return {
            "worker_id": self.worker_id,
            "capabilities": self.capabilities,
            "gpu_memory_mb": self.gpu_memory_mb,
        }


async def register_worker(kernel, worker_info: WorkerCapabilities):
    await kernel.scheduler.resources.register_node(
        worker_info.worker_id,
        {
            "gpu_memory_mb": worker_info.gpu_memory_mb,
            "capabilities": worker_info.capabilities,
            "status": "idle",
        },
    )
