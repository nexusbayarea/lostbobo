from __future__ import annotations

from backend.core.runtime.temporal.engine import TemporalEngine
from backend.core.services.observability_service import observability


class CircuitBreaker:
    _breakers: dict[str, dict] = {}

    @classmethod
    async def guard(cls, service: str):
        breaker = cls._breakers.setdefault(service, {"failures": 0, "state": "closed"})
        if breaker["state"] == "open":
            # Degrade mode
            await TemporalEngine.temporal().degrade_mode()
            raise RuntimeError(f"Circuit breaker open for {service}")

        try:
            yield
            breaker["failures"] = 0
        except Exception:
            breaker["failures"] += 1
            if breaker["failures"] >= 3:
                breaker["state"] = "open"
                observability().increment("circuit_breaker_tripped", tags={"service": service})
                # Automatic degrade actions
                await TemporalEngine.temporal().degrade_mode()
            raise
