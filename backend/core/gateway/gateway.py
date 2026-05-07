"""
Central Handshake/Gateway Layer — Enforces Compute Governance
Called on EVERY incoming request
"""

from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.governance.service import get_governance
from backend.core.kernel.kernel import get_kernel

log = logging.getLogger(__name__)


class GovernanceMiddleware(BaseHTTPMiddleware):
    """
    Enforces rate limiting, token budget, simulation throttling,
    and agent recursion protection on every request.
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Skip health checks and static routes
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        try:
            # Extract context from headers / JWT / query
            tenant_id = request.headers.get("x-tenant-id", "public")
            user_id = request.headers.get("x-user-id") or "anonymous"
            operation = self._infer_operation(request)

            # Estimate tokens (simple heuristic for now)
            body = await self._get_body_if_json(request)
            estimated_tokens = len(body.get("query", "")) // 4 + 200 if body else 400

            # Governance Check
            gov = get_governance()
            result = await gov.check(
                {
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                    "operation": operation,
                    "estimated_tokens": estimated_tokens,
                    "agent_hops": int(request.headers.get("x-agent-hops", 0)),
                    "path": request.url.path,
                }
            )

            if not result["allowed"]:
                log.warning(f"Governance blocked: {result['reason']} | user={user_id}")
                raise HTTPException(
                    status_code=429,
                    detail={"error": "compute_governance_violation", "reason": result["reason"], "retry_after": 60},
                )

            # Proceed with request
            response = await call_next(request)

            # Record actual usage
            duration = time.time() - start_time
            await self._record_usage(tenant_id, user_id, operation, duration)

            return response

        except HTTPException:
            raise
        except Exception as e:
            log.error(f"Gateway middleware error: {e}")
            raise HTTPException(status_code=500, detail="Internal governance error") from e

    def _infer_operation(self, request: Request) -> str:
        path = request.url.path.lower()
        if "/stream" in path or "stream" in request.query_params:
            return "stream"
        if "/simulate" in path or "/simulation" in path:
            return "simulation"
        if "/agent" in path:
            return "agent"
        if "/llm" in path or request.method == "POST":
            return "llm"
        return "retrieval"

    async def _get_body_if_json(self, request: Request) -> dict[str, Any]:
        try:
            if request.headers.get("content-type", "").startswith("application/json"):
                return await request.json()
        except Exception:
            pass
        return {}

    async def _record_usage(self, tenant_id: str, user_id: str, operation: str, duration: float):
        """Optional: persist usage metrics"""
        await get_kernel().execute(
            {
                "type": "MEMORY_RECORD",
                "payload": {
                    "type": "usage",
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                    "operation": operation,
                    "duration_ms": int(duration * 1000),
                },
            }
        )
