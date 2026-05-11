"""
backend/core/middleware/enforcement.py
Rate Limit + Cost Gate Middleware
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.middleware.rate_limiter import get_rate_limiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        limiter = get_rate_limiter()
        tenant_id = getattr(request.state, "tenant_id", "anon")
        path = request.url.path

        result = limiter.check(tenant_id, path)

        if not result.allowed:
            return Response(
                content="Rate limit exceeded",
                status_code=429,
                headers={"Retry-After": str(int(result.retry_after_seconds))},
            )

        return await call_next(request)


def register_middleware(app):
    app.add_middleware(RateLimitMiddleware)
