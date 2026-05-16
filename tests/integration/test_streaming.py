"""Streaming integration tests for SSE progressive retrieval."""

import httpx
import json
import pytest


BASE_URL = "http://localhost:8080"


@pytest.mark.asyncio
async def test_stream_states():
    token = await get_token()
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "GET",
            f"{BASE_URL}/api/v1/rag/stream?query=quantum+physics",
            headers={"Authorization": f"Bearer {token}"},
        ) as response:
            assert response.status_code == 200
            chunks = 0
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    data = json.loads(line[5:])
                    assert "documents" in data
                    chunks += 1
                    if chunks >= 3:
                        break
            assert chunks > 0, "Should receive at least 3 stream chunks"


@pytest.mark.asyncio
async def test_stream_multiple_queries():
    token = await get_token()
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ) as client:
        for query in ["quantum", "physics", "simulation"]:
            async with client.stream(
                "GET",
                f"{BASE_URL}/api/v1/rag/stream?query={query}",
            ) as response:
                assert response.status_code == 200
                chunks = 0
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        chunks += 1
                        if chunks >= 2:
                            break


@pytest.mark.asyncio
async def test_stream_requires_auth():
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "GET",
            f"{BASE_URL}/api/v1/rag/stream?query=test",
        ) as response:
            assert response.status_code == 401


async def get_token():
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/auth/token",
            json={"username": "admin", "password": "admin"},
        )
        return resp.json().get("token", "")
