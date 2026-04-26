from dataclasses import dataclass, field
import time


@dataclass
class Job:
    id: str
    payload: dict
    attempts: int = 0
    max_retries: int = 3
    created_at: float = field(default_factory=time.time)
