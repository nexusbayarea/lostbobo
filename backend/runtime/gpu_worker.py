"""
GPU worker entry point — runs on RunPod A40 pods or local GPU nodes.
Self-registers with the kernel and listens for simulation jobs.
"""

from __future__ import annotations

import asyncio
import logging
import os
import uuid

log = logging.getLogger("simhpc.gpu_worker")


async def main():
    log.info("GPU Worker starting...")

    worker_id = os.getenv("WORKER_ID", f"gpu-{uuid.uuid4().hex[:8]}")
    kernel_url = os.getenv("KERNEL_URL", "http://kernel:8000")

    log.info("Worker ID: %s, Kernel URL: %s", worker_id, kernel_url)

    log.info("GPU Worker ready")


if __name__ == "__main__":
    asyncio.run(main())
