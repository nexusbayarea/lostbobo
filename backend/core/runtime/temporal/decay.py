from __future__ import annotations

import math
import time
from typing import Any

from pydantic import BaseModel, Field

from backend.core.probability.prediction import Prediction
from backend.core.runtime.event_fabric.schema import SimHPCEvent
from backend.core.runtime.state_registry.service import WorldState
from backend.core.services.observability_service import observability
from backend.core.tracing import trace_context


class DecayConfig(BaseModel):
    """Configurable decay parameters per entity/signal type."""

    half_life_s: float = 86400.0  # 24 hours default
    regime_multiplier: dict[str, float] = Field(
        default_factory=lambda: {
            "normal": 1.0,
            "panic": 0.6,  # faster decay in panic
            "disruption": 0.3,  # very fast decay
        }
    )
    uncertainty_growth_factor: float = 0.3  # uncertainty increases as signal decays


class TemporalDecayEngine:
    """Centralized temporal decay engine."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def decay(cls) -> TemporalDecayEngine:
        return cls()

    def apply_decay(
        self,
        value: Any,
        uncertainty: float,
        half_life_s: float,
        last_updated: float,
        current_time: float,
        regime: str = "normal",
    ) -> tuple[Any, float]:
        """Apply exponential decay with regime awareness."""
        if not isinstance(value, (int, float)):
            return value, uncertainty  # non-numeric values unchanged

        age = current_time - last_updated
        if age <= 0:
            return value, uncertainty

        decay_factor = math.exp(-age / half_life_s)

        # Regime-aware acceleration
        multiplier = DecayConfig().regime_multiplier.get(regime, 1.0)
        effective_decay = decay_factor**multiplier

        decayed_value = value * effective_decay

        # Uncertainty grows as signal decays
        new_uncertainty = min(
            1.0,
            uncertainty + (1.0 - effective_decay) * DecayConfig().uncertainty_growth_factor,
        )

        return decayed_value, new_uncertainty

    async def propagate(self, state: WorldState, event: SimHPCEvent) -> WorldState:
        """Apply decay to entire WorldState + Entity Graph."""
        with trace_context("temporal.decay.propagate"):
            obs = observability()
            obs.increment("temporal_decay_applications_total")

            new_state = state.model_copy(deep=True)
            now = event.timestamp or time.time()

            for _key, ent in new_state.entities.items():
                if hasattr(ent, "prediction") and isinstance(ent.prediction, Prediction):
                    # Decay the Prediction object
                    decayed_value, new_unc = self.apply_decay(
                        ent.prediction.value,
                        ent.prediction.uncertainty,
                        getattr(ent, "half_life_s", 86400.0),
                        ent.last_updated,
                        now,
                        new_state.regime,
                    )
                    ent.prediction.value = decayed_value
                    ent.prediction.uncertainty = new_unc
                    ent.last_updated = now

            return new_state
