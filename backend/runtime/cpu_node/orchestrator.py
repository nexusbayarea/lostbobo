"""CPU Node Orchestrator with Response Caching + Node Handshake."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

from backend.runtime.a40.simulation import run_monte_carlo_simulation
from backend.runtime.api.reasoning_client import deepseek_api_call
from backend.runtime.graphrag.adaptive_retriever import fetch_exact, fetch_semantic
from backend.runtime.graphrag.context_compressor import compress_context_gemma
from backend.runtime.graphrag.nomic_classifier import classify_query


class ResponseCache:
    """Simple in-memory cache with TTL."""

    def __init__(self, ttl_minutes: int = 30):
        self.ttl = ttl_minutes * 60
        self._cache: dict[str, tuple[Any, float]] = {}

    async def get(self, query: str) -> Any | None:
        if query in self._cache:
            result, expiry = self._cache[query]
            if datetime.utcnow().timestamp() < expiry:
                return result
            del self._cache[query]
        return None

    async def store(self, query: str, response: Any):
        self._cache[query] = (response, datetime.utcnow().timestamp() + self.ttl)


class CPUNodeOrchestrator:
    def __init__(self):
        self.cache = ResponseCache(ttl_minutes=30)
        self.compressor = compress_context_gemma()

    async def stream_evaluate(self, query: str) -> AsyncGenerator[str | dict, None]:
        """Streaming version — yields tokens as they arrive."""
        cached = await self.cache.get(query)
        if cached:
            yield cached["response"]
            return

        query_type = await classify_query(query)
        context = await (fetch_exact(query) if query_type == "EXACT" else fetch_semantic(query))
        compressed = await self.compressor(context)

        partial = ""
        async for token in deepseek_api_call(compressed, stream=True):
            partial += token
            yield token

        simulation = await run_monte_carlo_simulation(query)

        final = {"response": partial, "simulation": simulation, "timestamp": datetime.utcnow().isoformat()}
        await self.cache.store(query, final)
        yield final

    async def process_query(self, query: str) -> dict[str, Any]:
        """Non-streaming version."""
        async for result in self.stream_evaluate(query):
            if isinstance(result, dict):
                return result
        return {"status": "error"}
