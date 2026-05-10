from __future__ import annotations

from pydantic import BaseModel, Field


class ResourceLimits(BaseModel):
    cpu_seconds: int = 60
    memory_mb: int = 512
    max_threads: int = 4
    max_graph_nodes: int = 2000


class PluginManifest(BaseModel):
    """Every plugin must declare this manifest."""

    name: str
    version: str
    description: str | None = None

    # Explicit capabilities (security model)
    permissions: list[str] = Field(default_factory=list)

    # Resource governance
    resource_limits: ResourceLimits = Field(default_factory=ResourceLimits)

    # Entry point for initialization
    entrypoint: str

    # Optional metadata
    tags: list[str] = Field(default_factory=list)
    author: str | None = None
    license: str = "internal"
