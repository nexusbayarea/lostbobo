"""
Canonical DAG Intermediate Representation.
Portable, serialisable, orchestrator-agnostic.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class IOType(str, Enum):
    """Supported data types for node inputs/outputs."""

    JSON = "json"
    TENSOR = "tensor"
    DATAFRAME = "dataframe"
    BINARY = "binary"
    ANY = "any"


class PortSpec(BaseModel):
    """Description of an input or output port."""

    name: str
    type: IOType = IOType.ANY
    description: str | None = None
    required: bool = True
    default: Any | None = None


class DAGNode(BaseModel):
    """
    A single node in the DAG.
    """

    id: str = Field(default_factory=lambda: uuid4().hex)
    node_type: str
    version: str = "1.0.0"
    inputs: list[PortSpec] = Field(default_factory=list)
    outputs: list[PortSpec] = Field(default_factory=list)
    resources: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DAGEdge(BaseModel):
    """
    Directed edge connecting an upstream node's output to a downstream node's input.
    """

    source_node: str
    source_port: str
    target_node: str
    target_port: str
    condition: str | None = None


class DAGGraph(BaseModel):
    """
    Complete DAG IR payload.
    """

    id: str = Field(default_factory=lambda: uuid4().hex)
    name: str = "unnamed"
    nodes: list[DAGNode] = Field(default_factory=list)
    edges: list[DAGEdge] = Field(default_factory=list)
    entry_node: str | None = None
    global_inputs: list[PortSpec] = Field(default_factory=list)
    global_outputs: list[PortSpec] = Field(default_factory=list)
