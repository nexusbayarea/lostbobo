from __future__ import annotations


class HealthProbe:
    def __init__(self, kernel):
        self.kernel = kernel

    async def status(self) -> dict:
        return {
            "healthy": True,
            "scheduler": "ok",
            "memory_fabric": "ok",
            "event_store": "ok",
            "protocol_bus": "ok",
            "plugins_loaded": len(self.kernel.plugins) if hasattr(self.kernel, "plugins") else 0,
            "uptime": self.kernel.uptime() if hasattr(self.kernel, "uptime") else 0,
        }
