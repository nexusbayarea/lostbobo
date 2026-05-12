from __future__ import annotations

import asyncio

import httpx

from backend.runtime.gpu_worker.executor import execute_job
from backend.runtime.gpu_worker.telemetry import TelemetryAgent


async def run_worker_loop(kernel_url: str, worker_id: str):
    agent = TelemetryAgent(kernel_url, worker_id)

    while True:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{kernel_url}/api/v1/worker/dequeue")
                if resp.status_code == 204:
                    await asyncio.sleep(2)
                    continue
                resp.raise_for_status()
                job = resp.json()

            result = await execute_job(job, agent)

            async with httpx.AsyncClient(timeout=30) as client:
                await client.post(
                    f"{kernel_url}/api/v1/worker/result",
                    json={
                        "execution_id": job["execution_id"],
                        "status": "completed",
                        "output": result,
                    },
                )
        except Exception as e:
            print(f"Error during job: {e}")
            await asyncio.sleep(1)
