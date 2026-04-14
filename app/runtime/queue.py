"""
Task Queue — Redis-backed distributed queue for multi-process execution

Provides shared queue across worker processes, enabling horizontal scaling.
"""

import json
from typing import Any, Optional

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class TaskQueue:
    def __init__(self, url: str = "redis://localhost:6379/0", key: str = "task_queue"):
        if not REDIS_AVAILABLE:
            raise ImportError("redis not installed. Run: pip install redis")
        self.r = redis.Redis.from_url(url, decode_responses=True)
        self.key = key

    def push(self, task: Any) -> None:
        self.r.rpush(self.key, json.dumps(task))

    def pop(self) -> Optional[dict]:
        item = self.r.lpop(self.key)
        if item:
            return json.loads(item)
        return None

    def empty(self) -> bool:
        return self.r.llen(self.key) == 0

    def __len__(self) -> int:
        return self.r.llen(self.key)
