"""Full CPU node integration test — validates all 7 steps together."""

import pytest
import httpx

BASE_URL = "http://localhost:8080"


@pytest.fixture
async def token():
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/auth/token",
            json={"username": "admin", "password": "admin"},
        )
        return resp.json()["token"]


@pytest.mark.asyncio
async def test_full_rag_flow(token):
    """Index → Retrieve → GraphQuery → Reason → Stream"""
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ) as client:
        resp = await client.post(
            f"{BASE_URL}/api/v1/rag/index",
            json={
                "text": "Quantum entanglement occurs when particles interact and share states.",
                "metadata": {
                    "topic": "physics",
                    "entities": ["quantum", "entanglement"],
                },
            },
        )
        assert resp.status_code == 200
        assert resp.json()["success"]

        resp = await client.post(
            f"{BASE_URL}/api/v1/rag/retrieve",
            json={
                "query": "What is quantum entanglement?",
                "top_k": 3,
            },
        )
        assert resp.status_code == 200
        docs = resp.json()["documents"]
        assert len(docs) > 0

        resp = await client.post(
            f"{BASE_URL}/api/v1/rag/graph-query",
            json={
                "query_type": "traverse",
                "start_node": "quantum",
                "max_depth": 1,
            },
        )
        assert resp.status_code == 200

        resp = await client.post(
            f"{BASE_URL}/api/v1/rag/reason",
            json={
                "context": docs,
                "prompt_template": "Explain quantum entanglement simply.",
            },
        )
        assert resp.status_code == 200
        assert len(resp.json()["answer"]) > 0

        async with client.stream(
            "GET", f"{BASE_URL}/api/v1/rag/stream?query=quantum"
        ) as response:
            chunks = 0
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    chunks += 1
                    if chunks >= 3:
                        break
            assert chunks > 0


@pytest.mark.asyncio
async def test_auth_required():
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/api/v1/rag/retrieve", json={"query": "test"}
        )
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_tenant_isolation(token):
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ) as client:
        await client.post(
            f"{BASE_URL}/api/v1/rag/index",
            json={
                "text": "Tenant A document",
                "tenant_id": "tenant-a",
            },
        )
        await client.post(
            f"{BASE_URL}/api/v1/rag/retrieve",
            json={
                "query": "tenant document",
                "tenant_id": "tenant-a",
            },
        )
        resp_b = await client.post(
            f"{BASE_URL}/api/v1/rag/retrieve",
            json={
                "query": "tenant document",
                "tenant_id": "tenant-b",
            },
        )
        docs_b = resp_b.json()["documents"]
        tenant_b_has_a = any("Tenant A" in d.get("text", "") for d in docs_b)
        assert not tenant_b_has_a


@pytest.mark.asyncio
async def test_plugin_capability(token):
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ) as client:
        resp = await client.post(
            f"{BASE_URL}/api/v1/simulate",
            json={
                "capability": "ev.thermal",
                "payload": {"battery_temp": 30},
            },
        )
        assert resp.status_code == 200
        assert "job_id" in resp.json()


@pytest.mark.asyncio
async def test_event_system(token):
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}
    ) as client:
        resp = await client.post(
            f"{BASE_URL}/api/v1/events/test",
            json={
                "event_type": "integration.test",
                "payload": {"step": 8},
            },
        )
        assert resp.status_code == 200
