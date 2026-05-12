"""
A40 GPU Worker - Stateless Deterministic Execution Appliance
"""

from __future__ import annotations

import asyncio
import os

from backend.runtime.gpu_worker.registration import register_worker
from backend.runtime.gpu_worker.worker import run_worker_loop


async def main():
    from deployments.runtime.bootstrap.infisical_bootstrap import bootstrap_secrets

    await bootstrap_secrets()

    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU not available")
    print(f"GPU: {torch.cuda.get_device_name(0)}")

    worker_id = os.environ.get("WORKER_ID", "gpu-a40-1")
    kernel_url = os.environ["KERNEL_URL"]

    await register_worker(kernel_url, worker_id)

    await run_worker_loop(kernel_url, worker_id)


if __name__ == "__main__":
    asyncio.run(main())
