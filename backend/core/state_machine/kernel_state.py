from __future__ import annotations

from enum import Enum


class KernelState(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    CHECKPOINTING = "checkpointing"
    PAUSED = "paused"
    REPLAYING = "replaying"
    FAILED = "failed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
