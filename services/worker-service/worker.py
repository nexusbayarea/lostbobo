"""
Worker Service — background job processor.
Reads from Redis queues, executes tasks using kernel capabilities.
"""

import asyncio
import json
import logging
import os

import redis.asyncio as aioredis
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
RAG_HOST = os.getenv("RAG_SERVICE_HOST", "rag-service")
RAG_PORT = os.getenv("RAG_SERVICE_PORT", "50051")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

QUEUES = ["queue:simulation", "queue:indexing", "queue:graph", "queue:default"]


class JobProcessor:
    def __init__(self):
        self.redis = None
        self.http = httpx.AsyncClient(timeout=120.0)

    async def start(self):
        self.redis = await aioredis.from_url(REDIS_URL)
        logger.info(f"Worker listening on queues: {QUEUES}")

    async def process_job(self, queue: str, job_data: dict):
        job_type = queue.split(":")[-1]
        job_id = job_data.get("job_id", "unknown")
        logger.info(f"Processing {job_type} job {job_id}")

        if job_type == "indexing":
            await self.handle_indexing(job_data)
        elif job_type == "simulation":
            await self.handle_simulation(job_data)
        elif job_type == "graph":
            await self.handle_graph(job_data)
        else:
            await self.handle_default(job_data)

        await self.redis.set(f"job:{job_id}:status", "completed")
        logger.info(f"Job {job_id} completed")

    async def handle_indexing(self, job: dict):
        text_to_index = job.get("text", "")
        response = await self.http.post(
            f"{OLLAMA_HOST}/api/embed",
            json={"model": "nomic-embed-text:v2-moe", "input": [text_to_index]},
        )
        response.raise_for_status()

    async def handle_simulation(self, job: dict):
        capability = job.get("capability", "")
        payload = job.get("payload", {})
        logger.info(f"Simulation job: {capability} with payload {payload}")
        await asyncio.sleep(0.1)

    async def handle_graph(self, job: dict):
        logger.info(f"Graph job: {job.get('action', 'unknown')}")

    async def handle_default(self, job: dict):
        logger.info(f"Default job: {job}")

    async def run(self):
        await self.start()
        while True:
            for queue in QUEUES:
                result = await self.redis.brpop(queue, timeout=1)
                if result:
                    _, data = result
                    try:
                        job = json.loads(data)
                        await self.process_job(queue, job)
                    except Exception as e:
                        logger.error(f"Failed to process job: {e}")
            await asyncio.sleep(0.1)


async def main():
    processor = JobProcessor()
    await processor.run()


if __name__ == "__main__":
    asyncio.run(main())
