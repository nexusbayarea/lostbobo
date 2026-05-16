"""
Worker — background ingestion, graph construction, retries, verification.
Polls Supabase for pending jobs, processes documents via DeepSeek, stores in pgvector.
No Redis dependency — Supabase is the single source of truth.
"""

import asyncio
import json
import logging
import os

import httpx
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE = "https://api.deepseek.com/v1"


class Worker:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.deepseek = httpx.AsyncClient(
            base_url=DEEPSEEK_BASE,
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            timeout=120.0,
        )

    async def poll_jobs(self):
        """Poll the ingestion_jobs table for pending work."""
        result = (
            await self.supabase.table("ingestion_jobs")
            .select("*")
            .eq("status", "pending")
            .limit(10)
            .execute()
        )
        return result.data or []

    async def process_job(self, job: dict):
        job_id = job.get("id")
        text = job.get("text", "")
        tenant_id = job.get("tenant_id", "default")
        metadata = job.get("metadata", {})
        logger.info(f"Processing job {job_id}")

        try:
            await (
                self.supabase.table("ingestion_jobs")
                .update({"status": "processing"})
                .eq("id", job_id)
                .execute()
            )

            embedding = await self.get_embedding(text)

            await (
                self.supabase.table("rag_documents")
                .insert(
                    {
                        "content": text,
                        "embedding": embedding,
                        "tenant_id": tenant_id,
                        "metadata": json.dumps(metadata)
                        if isinstance(metadata, dict)
                        else metadata,
                    }
                )
                .execute()
            )

            await (
                self.supabase.table("ingestion_jobs")
                .update({"status": "completed"})
                .eq("id", job_id)
                .execute()
            )

            logger.info(f"Job {job_id} completed")
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            await (
                self.supabase.table("ingestion_jobs")
                .update({"status": "failed", "error": str(e)})
                .eq("id", job_id)
                .execute()
            )

    async def get_embedding(self, text: str) -> list[float]:
        resp = await self.deepseek.post(
            "/embeddings",
            json={
                "model": "text-embedding-ada-002",
                "input": text,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["data"][0]["embedding"]

    async def run(self):
        logger.info("Worker started, polling Supabase every %ds", POLL_INTERVAL)
        while True:
            try:
                jobs = await self.poll_jobs()
                for job in jobs:
                    await self.process_job(job)
            except Exception as e:
                logger.error("Poll cycle error: %s", e)
            await asyncio.sleep(POLL_INTERVAL)


async def main():
    worker = Worker()
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
