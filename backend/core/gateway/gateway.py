import logging
import uuid

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.auth.models import AuthContext, Role
from backend.core.auth.policy_engine import get_policy_engine
from backend.core.governance.service import get_governance
from backend.core.security.supabase import get_supabase_client

log = logging.getLogger(__name__)


class SecurityGatewayMiddleware(BaseHTTPMiddleware):
    """
    Full control plane: AuthN → Tenant → AuthZ → Governance
    """

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Skip public routes
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json", "/metrics"]:
            return await call_next(request)

        try:
            # 1. Authentication (AuthN)
            auth_context = await self._authenticate(request)

            # Attach to request state for downstream use
            request.state.auth = auth_context
            request.state.tenant_id = auth_context.tenant_id

            # 2. Authorization (AuthZ) + Policy Check
            if not await self._authorize(request, auth_context):
                raise HTTPException(status_code=403, detail="Forbidden by policy")

            # 3. Governance Check (Rate limits, tokens, simulation throttle, etc.)
            gov = get_governance()
            gov_result = await gov.check(
                {
                    "tenant_id": auth_context.tenant_id,
                    "user_id": auth_context.user_id,
                    "operation": self._infer_operation(request),
                    "estimated_tokens": self._estimate_tokens(request),
                    "agent_hops": int(request.headers.get("x-agent-hops", 0)),
                }
            )

            if not gov_result["allowed"]:
                raise HTTPException(
                    status_code=429, detail={"error": "compute_governance_violation", "reason": gov_result["reason"]}
                )

            # Proceed
            response = await call_next(request)
            return response

        except HTTPException as e:
            raise e
        except Exception as e:
            log.error(f"Security gateway failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Security layer error") from e

    async def _authenticate(self, request: Request) -> AuthContext:
        """JWT + Supabase AuthN"""
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            raise HTTPException(status_code=401, detail="Missing token")

        supabase = get_supabase_client()
        try:
            # Validate JWT via Supabase
            user = supabase.auth.get_user(token)
            if not user or not user.user:
                raise HTTPException(status_code=401, detail="Invalid token")

            # Build context
            roles = [Role(role) for role in user.user.user_metadata.get("roles", ["viewer"])]
            tenant_id = user.user.user_metadata.get("tenant_id", "public")

            return AuthContext(
                user_id=user.user.id,
                tenant_id=tenant_id,
                roles=roles,
                agent_id=request.headers.get("x-agent-id"),
                request_id=request.state.request_id,
            )
        except Exception as e:
            raise HTTPException(status_code=401, detail="Authentication failed") from e

    async def _authorize(self, request: Request, ctx: AuthContext) -> bool:
        """Contextual + Compute-aware Authorization"""
        policy = get_policy_engine()
        policy_result = await policy.evaluate(
            ctx,
            {
                "action": "execute",
                "resource": self._infer_operation(request),
                "estimated_cost": 50 if "simulation" in request.url.path else 5,
                "estimated_tokens": 800,
            },
        )
        return policy_result["allowed"]

    def _infer_operation(self, request: Request) -> str:
        path = request.url.path.lower()
        if "/stream" in path:
            return "stream"
        if "/simulate" in path:
            return "simulation"
        if "/agent" in path:
            return "agent"
        return "llm" if request.method == "POST" else "retrieval"

    def _estimate_tokens(self, request: Request) -> int:
        return 800
