from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from uuid import uuid4


class ProvenanceNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    node_type: str                          # execution_run, gpu_allocation, forecast, agent_action, event, hardware_node
    entity_id: str
    timestamp: datetime
    version: str = "v1"
    metadata: Dict = Field(default_factory=dict)


class ProvenanceEdge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str
    target_id: str
    relation: str                           # SCHEDULED_ON, PRODUCED, CONTRIBUTED_TO, RESOLVED_AS, ATTESTED_BY
    weight: float = 1.0
    timestamp: datetime
    metadata: Dict = Field(default_factory=dict)


class ExecutionProvenanceGraph(BaseModel):
    run_id: str
    nodes: Dict[str, ProvenanceNode] = Field(default_factory=dict)
    edges: List[ProvenanceEdge] = Field(default_factory=list)
    root_node: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
