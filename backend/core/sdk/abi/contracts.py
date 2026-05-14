from __future__ import annotations
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ExecutionContract(BaseModel):
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int = 300
    max_retries: int = 0
    retry_delay_seconds: float = 1.0
    idempotent: bool = True
    deterministic: bool = True
    required_capabilities: list[str] = Field(default_factory=list)
    required_resources: list[str] = Field(default_factory=list)


class ExecutionResult(BaseModel):
    success: bool
    outputs: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    execution_time_seconds: float = 0.0
    retry_attempt: int = 0
