from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from app.models.version import CURRENT_JOB_SCHEMA_VERSION


def generate_idempotency_key(payload: dict) -> str:
    """Generate deterministic idempotency key from job input params."""
    import hashlib
    import json

    normalized = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(normalized.encode()).hexdigest()[:32]


class JobProgress(BaseModel):
    percent: int = 0
    stage: Optional[str] = None
    current: Optional[int] = None
    total: Optional[int] = None


class JobResult(BaseModel):
    summary: Optional[str] = None
    output: Optional[Dict[str, Any]] = None


class Job(BaseModel):
    schema_version: int = CURRENT_JOB_SCHEMA_VERSION

    id: str
    user_id: str

    status: str = (
        "queued"  # queued | running | completed | failed | retrying | cancelled
    )
    progress: JobProgress = JobProgress()

    input_params: Dict[str, Any] = {}
    scenario_name: Optional[str] = None

    idempotency_key: Optional[str] = None

    result: Optional[JobResult] = None
    error: Optional[str] = None

    retries: int = 0

    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    def generate_key(self) -> str:
        """Generate idempotency key from input params if not set."""
        if self.idempotency_key:
            return self.idempotency_key
        return generate_idempotency_key(self.input_params)

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "Job":
        return cls(**data)
