from __future__ import annotations

import os

import httpx
import torch


async def register_worker(kernel_url: str, worker_id: str):
    capabilities = {
        "gpu": "a40",
        "cuda_version": torch.version.cuda,
        "torch_version": torch.__version__,
        "vram_mb": torch.cuda.get_device_properties(0).total_memory // (1024 * 1024),
        "plugin_abi": "1.0.0",
        "runtime_hash": os.environ.get("SIMHPC_IMAGE_HASH", "dev"),
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"{kernel_url}/api/v1/worker/register",
            json={"worker_id": worker_id, "capabilities": capabilities},
        )
        resp.raise_for_status()
        print(f"Worker registered: {resp.json()}")
