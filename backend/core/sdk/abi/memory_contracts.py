from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field


class MemoryAccessPolicy(BaseModel):
    tier: str
    namespace: str
    read_allowed: bool = False
    write_allowed: bool = False
    evict_allowed: bool = False
    ttl_seconds: Optional[int] = None
    confidence_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class MemoryFabricAccess(BaseModel):
    policies: List[MemoryAccessPolicy] = Field(default_factory=list)
    default_ttl_seconds: Optional[int] = None
    max_namespaces: int = 10


class MemoryKey(BaseModel):
    namespace: str
    key: str
    tier: str = "episodic"


class MemoryEntry(BaseModel):
    key: MemoryKey
    value: bytes
    ttl_seconds: Optional[int] = None
    plugin_source: str = ""
