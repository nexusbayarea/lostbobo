from __future__ import annotations
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class DAGNodeInput(BaseModel):
    name: str
    type: str
    required: bool = True
    description: str = ""
    default: Any = None
    json_schema: Dict[str, Any] = Field(default_factory=dict)


class DAGNodeOutput(BaseModel):
    name: str
    type: str
    description: str = ""
    json_schema: Dict[str, Any] = Field(default_factory=dict)


class DAGNodeContract(BaseModel):
    model_config = {"protected_namespaces": ()}
    node_type: str
    version: str = "1.0.0"
    inputs: List[DAGNodeInput] = Field(default_factory=list)
    outputs: List[DAGNodeOutput] = Field(default_factory=list)
    deterministic: bool = True
    idempotent: bool = True
    max_retries: int = 0
    timeout_seconds: int = 300
    required_capabilities: List[str] = Field(default_factory=list)


class DAGEdge(BaseModel):
    source: str
    target: str
    data_mapping: Dict[str, str] = Field(default_factory=dict)


class DAGExecutionPlan(BaseModel):
    nodes: List[DAGNodeContract] = Field(default_factory=list)
    edges: List[DAGEdge] = Field(default_factory=list)
    max_concurrency: int = 1
    timeout_seconds: int = 3600
