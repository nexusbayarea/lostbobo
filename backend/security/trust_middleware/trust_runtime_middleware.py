from fastapi import Request
from fastapi.responses import JSONResponse

from backend.app.kernel.command_bus import command_bus


class TrustRuntimeMiddleware:
    async def __call__(self, request: Request, call_next):
        tenant_id = request.headers.get("X-Tenant-ID")
        body = await request.json() if request.method in ["POST", "PUT"] else {}

        # All logic through Kernel Command Bus
        result = await command_bus.route(
            {
                "type": "TRUST_VERIFY",
                "payload": {"input": body, "tenant_id": tenant_id, "job_id": request.headers.get("X-Job-ID")},
            }
        )

        if result.decision == "BLOCK":
            return JSONResponse({"error": "Blocked by Trust Runtime", "reason": result.risk_flags}, status_code=403)

        # Attach certificate header from Supabase
        response = await call_next(request)
        response.headers["X-Trust-Certificate"] = result.certificate_id
        return response
