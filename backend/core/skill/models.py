from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import BaseModel, Field


class CapabilityDefinition(BaseModel):
    """Runtime metadata for a registered capability."""

    name: str
    plugin_name: str
    version: str = "1.0.0"
    handler: Callable[..., Awaitable[Any]]  # async callable
    input_schema: dict[str, Any] | None = None  # JSON Schema for validation
    output_schema: dict[str, Any] | None = None
    permissions: list[str] = Field(default_factory=list)  # required permissions
    dependencies: list[str] = Field(default_factory=list)  # other capability names
    tags: list[str] = Field(default_factory=list)
    deterministic: bool = True
    timeout_seconds: int = 300


class SkillDefinition(BaseModel):
    """A logical grouping of capabilities that form a higher-order task."""

    name: str
    description: str = ""
    capability_names: list[str] = Field(default_factory=list)
    plugin_name: str = ""


class ToolDefinition(BaseModel):
    """A low-level tool exported by a plugin."""

    name: str
    plugin_name: str
    function: Callable[..., Any]  # can be sync or async
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    tags: list[str] = Field(default_factory=list)
