import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.kernel.command_bus import command_bus


class OpenTelemetryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        tenant_id = request.headers.get("X-Tenant-ID", "unknown")

        response = await call_next(request)

        duration = time.time() - start_time

        # Record via Kernel
        await command_bus.route(
            {
                "type": "RECORD_OBSERVABILITY",
                "payload": {
                    "type": "request",
                    "method": request.method,
                    "route": request.url.path,
                    "status": response.status_code,
                    "duration": duration,
                    "tenant_id": tenant_id,
                },
            }
        )

        return response
