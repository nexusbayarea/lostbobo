"""
backend/core/middleware/rate_limiter.py
Sliding Window Rate Limiter (Supabase-backed)
"""

import time
from dataclasses import dataclass

from backend.app.core.supabase import get_supabase_client


@dataclass
class RateLimitConfig:
    requests_per_minute: int
    burst_capacity: int
    window_seconds: int = 60


TIER_LIMITS = {
    "free": RateLimitConfig(60, 10),
    "professional": RateLimitConfig(300, 50),
    "enterprise": RateLimitConfig(1000, 200),
    "defense": RateLimitConfig(2000, 500),
}

ENDPOINT_OVERRIDES = {
    "/api/v1/ml/infer": RateLimitConfig(10, 3),
    "/api/v1/certificates/issue": RateLimitConfig(20, 5),
    "/api/v1/hardware/schedule": RateLimitConfig(30, 10),
}


@dataclass
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    retry_after_seconds: float
    algorithm: str


class RateLimiter:
    def __init__(self):
        self._db = get_supabase_client()

    def check(self, tenant_id: str, endpoint: str, sla_tier: str = "free") -> RateLimitResult:
        cfg = ENDPOINT_OVERRIDES.get(endpoint) or TIER_LIMITS.get(sla_tier, TIER_LIMITS["free"])

        # Call Supabase RPC
        now = time.time()
        window_start = now - cfg.window_seconds

        # RPC returns {"count": int, "allowed": bool}
        response = self._db.rpc(
            "rate_limit_sliding_window",
            {
                "p_tenant_id": tenant_id,
                "p_endpoint": endpoint,
                "p_window_start": window_start,
                "p_bucket": int(now),
                "p_limit": cfg.requests_per_minute,
            },
        ).execute()

        result = response.data
        return RateLimitResult(
            allowed=result["allowed"],
            limit=cfg.requests_per_minute,
            remaining=max(0, cfg.requests_per_minute - result["count"]),
            retry_after_seconds=0 if result["allowed"] else 1.0,
            algorithm="sliding_window_sql",
        )


_limiter = None


def get_rate_limiter() -> RateLimiter:
    global _limiter
    if _limiter is None:
        _limiter = RateLimiter()
    return _limiter
