"""Integration tests for SimHPC Gamma deployment."""

import httpx
import pytest


@pytest.mark.integration
class TestGatewayHealth:
    def test_health_endpoint(self, gateway_url="http://localhost:8080"):
        response = httpx.get(f"{gateway_url}/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_returns_timestamp(self, gateway_url="http://localhost:8080"):
        response = httpx.get(f"{gateway_url}/health", timeout=10)
        data = response.json()
        assert "timestamp" in data


@pytest.mark.integration
class TestRAGService:
    def test_retrieve_requires_auth(self, gateway_url="http://localhost:8080"):
        response = httpx.post(
            f"{gateway_url}/api/v1/rag/retrieve",
            json={"query": "test", "top_k": 1},
            timeout=10,
        )
        assert response.status_code == 401

    def test_index_requires_auth(self, gateway_url="http://localhost:8080"):
        response = httpx.post(
            f"{gateway_url}/api/v1/rag/index",
            json={"text": "test document"},
            timeout=10,
        )
        assert response.status_code == 401
