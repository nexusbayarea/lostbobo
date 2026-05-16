"""
GPU Worker — Deterministic simulation runtime for physics/forecasting on A40.
Simulation plane only: no embeddings, no RAG, no lightweight LLMs.
"""

import asyncio
import json
import logging
import os
from concurrent import futures

import grpc
import redis.asyncio as aioredis
from supabase import create_client, Client

from services.proto import simulation_pb2, simulation_pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gpu-worker")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
KERNEL_HOST = os.getenv("KERNEL_HOST", "kernel")
KERNEL_PORT = os.getenv("KERNEL_PORT", "50054")
CUDA_DEVICE = os.getenv("CUDA_VISIBLE_DEVICES", "0")
PORT = os.getenv("PORT", "50053")


class SimulationServicer(simulation_pb2_grpc.SimulationServiceServicer):
    def __init__(self):
        self.redis = None
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.jobs = {}

    async def start(self):
        self.redis = await aioredis.from_url(REDIS_URL)
        logger.info("GPU Worker connected to Redis")

    async def RunSimulation(self, request, context):
        job_id = request.job_id
        self.jobs[job_id] = {"status": "running", "progress": 0.0}
        await self.redis.set(f"job:{job_id}:status", "running")
        try:
            result = await self.execute_simulation(request.capability, request.payload)
            self.jobs[job_id] = {"status": "completed", "progress": 1.0}
            await self.redis.set(f"job:{job_id}:status", "completed")
            return simulation_pb2.SimulationResponse(
                job_id=job_id,
                status="completed",
                message=result,
            )
        except Exception as e:
            self.jobs[job_id] = {"status": "failed", "error": str(e)}
            await self.redis.set(f"job:{job_id}:status", "failed")
            return simulation_pb2.SimulationResponse(
                job_id=job_id,
                status="failed",
                message=str(e),
            )

    async def GetStatus(self, request, context):
        job = self.jobs.get(request.job_id, {})
        return simulation_pb2.StatusResponse(
            job_id=request.job_id,
            status=job.get("status", "unknown"),
            progress=job.get("progress", 0.0),
            error=job.get("error", ""),
        )

    async def StreamResults(self, request, context):
        job_id = request.job_id
        for step in range(10):
            await asyncio.sleep(0.5)
            yield simulation_pb2.SimulationResult(
                job_id=job_id,
                step=step,
                data=json.dumps({"step": step, "value": step * step}).encode(),
                metadata={"progress": str((step + 1) / 10)},
            )

    async def execute_simulation(self, capability: str, payload: bytes) -> str:
        logger.info(f"Executing capability: {capability} on GPU {CUDA_DEVICE}")
        await asyncio.sleep(1.0)
        return f"Simulation {capability} completed on GPU {CUDA_DEVICE}"


async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = SimulationServicer()
    await servicer.start()
    simulation_pb2_grpc.add_SimulationServiceServicer_to_server(servicer, server)
    server.add_insecure_port(f"[::]:{PORT}")
    await server.start()
    logger.info(f"GPU Worker listening on port {PORT}")
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
