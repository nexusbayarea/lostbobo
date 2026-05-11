from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from backend.app.api.auth import get_current_user
from backend.core.tenant_isolation.tenant import (
    TenantContext,
    reset_tenant_context,
    set_tenant_context,
)

_PUBLIC_PREFIXES = (
    "/health",
    "/metrics",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/api/v1/auth/login",
)


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if any(path.startswith(p) for p in _PUBLIC_PREFIXES):
            return await call_next(request)

        # Extract token and tenant
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing token"})

        # Get user context
        try:
            # We need to bypass Depends inside middleware, calling get_current_user directly
            # This requires a slightly different approach as get_current_user expects credentials
            from fastapi.security import HTTPAuthorizationCredentials

            token = auth[7:].strip()
            user = await get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token))
            tenant_id = user.get("user_id", "default_tenant")
        except Exception:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})

        token_var = set_tenant_context(tenant_id)
        request.state.tenant = TenantContext(tenant_id, user["user_id"], user.get("role", "user"))

        try:
            return await call_next(request)
        finally:
            reset_tenant_context(token_var)
