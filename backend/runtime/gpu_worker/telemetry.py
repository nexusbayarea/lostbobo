from __future__ import annotations

import time

import httpx


class TelemetryAgent:
    def __init__(self, kernel_url: str, worker_id: str):
        self.kernel_url = kernel_url
        self.worker_id = worker_id

    async def emit(self, execution_id: str, event_type: str, data: dict):
        async with httpx.AsyncClient(timeout=5) as client:
            try:
                await client.post(
                    f"{self.kernel_url}/api/v1/worker/telemetry",
                    json={
                        "worker_id": self.worker_id,
                        "execution_id": execution_id,
                        "event_type": event_type,
                        "timestamp": time.time(),
                        "data": data,
                    },
                )
            except Exception:
                pass
