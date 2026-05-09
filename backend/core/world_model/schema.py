"""WorldState — probabilistic digital twin with explicit uncertainty."""

from __future__ import annotations

import time
import uuid
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from backend.core.runtime.event_fabric.schema import SimHPCEvent


class EntityVariable(BaseModel):
    value: Any
    uncertainty: float = Field(default=0.0, ge=0.0, le=1.0)
    half_life_s: float = Field(default=86400.0)
    last_updated: float = Field(default_factory=time.time)
    provenance_event_id: str = ""


class UncertaintyField(BaseModel):
    mean: float
    std: float = 0.0
    source_reliability: float = 1.0
    contributing_events: list[str] = Field(default_factory=list)


class WorldState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=time.time)
    causal_id: str = "genesis"
    regime: str = "normal"

    entities: dict[str, EntityVariable] = Field(default_factory=dict)
    uncertainty: dict[str, UncertaintyField] = Field(default_factory=dict)
    provenance: dict[str, str] = Field(default_factory=dict)

    def apply_event(self, event: SimHPCEvent) -> WorldState:  # noqa: F821
        new_state = self.model_copy(deep=True)
        new_state.timestamp = max(new_state.timestamp, event.timestamp)
        new_state.causal_id = event.causal_id

        for key, change in event.payload.get("entities", {}).items():
            if key not in new_state.entities:
                new_state.entities[key] = EntityVariable(value=change.get("value"))
            else:
                ent = new_state.entities[key]
                ent.value = change.get("value", ent.value)
                ent.uncertainty = change.get("uncertainty", ent.uncertainty)
                ent.last_updated = event.timestamp
                ent.provenance_event_id = event.event_id

        new_state.provenance[f"event:{event.event_id}"] = event.provenance_hash or ""
        return new_state
