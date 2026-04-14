"""
Result Store — Redis-backed shared state for distributed execution

Provides shared result storage across worker processes.
"""

import json
from typing import Any, Optional

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class ResultStore:
    def __init__(self, url: str = "redis://localhost:6379/0", key: str = "results"):
        if not REDIS_AVAILABLE:
            raise ImportError("redis not installed. Run: pip install redis")
        self.r = redis.Redis.from_url(url, decode_responses=True)
        self.key = key

    def set(self, name: str, value: Any) -> None:
        self.r.hset(self.key, name, json.dumps(value))

    def get(self, name: str) -> Optional[dict]:
        val = self.r.hget(self.key, name)
        return json.loads(val) if val else None

    def exists(self, name: str) -> bool:
        return self.r.hexists(self.key, name)

    def all(self) -> dict:
        data = self.r.hgetall(self.key)
        return {k: json.loads(v) for k, v in data.items()}

    def clear(self) -> None:
        self.r.delete(self.key)
