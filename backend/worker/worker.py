#!/usr/bin/env python3
"""
SimHPC Physics Worker — Full DAG Consumer
"""

import asyncio
import sys
from pathlib import Path

if str(Path(__file__).resolve().parents[2]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.runtime.dag_executor import execute_dag
from backend.runtime.job import Job
from backend.runtime.kernel import KERNEL
from backend.runtime.queue import QUEUE


async def process_job(job: Job):
    print(f"[Worker] Processing job {job.id} | Payload: {job.payload.get('type')}")
    try:
        if job.payload.get("type") == "dag":
            await execute_dag()
        else:
            result = KERNEL.execute(job.payload)
            print(f"[Worker] Job {job.id} result: {result.get('status')}")
        return True
    except Exception as e:
        print(f"[Worker] Job {job.id} failed: {e}")
        return False


async def main():
    print("[Worker] SimHPC Physics Worker (DAG Mode) Started")

    while True:
        try:
            job = await QUEUE.dequeue() if hasattr(QUEUE, "dequeue") else None
            if not job:
                await asyncio.sleep(1)
                continue

            await process_job(job)

        except Exception as e:
            print(f"[Worker] Loop error: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
