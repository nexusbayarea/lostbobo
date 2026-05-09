from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from backend.core.runtime.event_fabric.schema import SimHPCEvent


class Provenance(BaseModel):
    event_id: str
    source: str
    weight: float = 1.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class Prediction(BaseModel):
    """First-class probabilistic primitive for the entire runtime."""

    id: str = Field(default_factory=lambda: str(uuid4()))

    value: float  # main probability / expected value
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    uncertainty: float = Field(default=0.0, ge=0.0, le=1.0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    horizon: datetime | None = None
    regime: str | None = None

    provenance: list[Provenance] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def expected_value(self) -> float:
        return self.value * self.confidence

    def variance(self) -> float:
        return self.uncertainty**2

    def entropy(self) -> float:
        import math

        p = max(min(self.value, 1 - 1e-9), 1e-9)
        return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))

    def calibrate(self, delta: float) -> Prediction:
        adjusted = max(0.0, min(1.0, self.value + delta))
        return self.model_copy(
            update={
                "value": adjusted,
                "metadata": {
                    **self.metadata,
                    "calibrated": True,
                    "calibration_delta": delta,
                },
            }
        )

    def with_provenance(self, event: SimHPCEvent) -> Prediction:
        self.provenance.append(
            Provenance(
                event_id=event.event_id,
                source=event.source_plugin,
                weight=event.confidence,
                metadata=event.payload,
            )
        )
        return self
