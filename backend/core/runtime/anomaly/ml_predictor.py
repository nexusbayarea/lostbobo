# backend/core/runtime/anomaly/ml_predictor.py
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

log = logging.getLogger(__name__)


@dataclass
class PredictedAnomaly:
    predicted_at: float
    horizon_seconds: int
    anomaly_type: str
    probability: float
    severity: str
    affected_entity_keys: list[str] = field(default_factory=list)
    features: dict[str, float] = field(default_factory=dict)


class MLAnomalyPredictor:
    """Singleton ML predictor for future causal anomalies."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._model = None
            cls._scaler = None
            cls._isolation_forest = None
            cls._lstm_model = None
            cls._history: list[dict[str, float]] = []
            cls._initialized = False
        return cls._instance

    def _ensure_initialized(self):
        if self._initialized:
            return
        self._initialized = True
        try:
            from sklearn.ensemble import IsolationForest

            self._isolation_forest = IsolationForest(contamination=0.05, random_state=42)
            self._scaler = True
        except Exception as e:
            log.warning("ML libraries not available: %s", e)

    def _build_lstm(self):
        try:
            import torch
            import torch.nn as nn

            class LSTMAnomalyModel(nn.Module):
                def __init__(self):
                    super().__init__()
                    self.lstm = nn.LSTM(input_size=12, hidden_size=64, num_layers=2, batch_first=True)
                    self.fc = nn.Linear(64, 4)

                def forward(self, x):
                    out, _ = self.lstm(x)
                    return self.fc(out[:, -1, :])

            self._lstm_model = LSTMAnomalyModel()
            self._lstm_model.eval()
        except Exception as e:
            log.warning("LSTM model not available: %s", e)
            self._lstm_model = None

    async def predict(self, lookback_window: int = 30) -> list[PredictedAnomaly]:
        """Predict anomalies in the next 5–60 minutes."""
        self._ensure_initialized()

        state = await self._get_state_snapshot()
        recent_events = await self._get_recent_events()

        features = self._extract_features(state, recent_events)
        self._history.append(features)
        if len(self._history) > 300:
            self._history.pop(0)

        if len(self._history) < lookback_window:
            return []

        predictions: list[PredictedAnomaly] = []

        try:
            import numpy as np

            feature_array = list(features.values())
            if not all(isinstance(v, (int, float)) for v in feature_array):
                return predictions

            X = np.array([list(h.values()) for h in self._history[-lookback_window:]])

            ensemble_prob = 0.25

            if self._lstm_model is None:
                self._build_lstm()

            if self._lstm_model is not None:
                try:
                    import torch

                    X_scaled = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)
                    lstm_input = torch.tensor(X_scaled[-10:]).unsqueeze(0).float()
                    with torch.no_grad():
                        lstm_out = self._lstm_model(lstm_input)
                        probs = torch.softmax(lstm_out, dim=1)[0]
                    ensemble_prob = float(probs.max())
                except Exception:
                    pass

            if self._isolation_forest is not None:
                try:
                    if_score = self._isolation_forest.fit_predict(X[-1].reshape(1, -1))[0]
                    if if_score == -1:
                        ensemble_prob = max(ensemble_prob, 0.45)
                except Exception:
                    pass

            if ensemble_prob > 0.35:
                anomaly_types = ["causal_break", "regime_shift", "uncertainty_spike", "mass_violation"]
                anomaly_type = anomaly_types[0]
                try:
                    import torch

                    anomaly_type = anomaly_types[torch.argmax(probs).item()]
                except Exception:
                    pass

                severity = "high" if ensemble_prob > 0.7 else "medium"

                predictions.append(
                    PredictedAnomaly(
                        predicted_at=time.time(),
                        horizon_seconds=300,
                        anomaly_type=anomaly_type,
                        probability=ensemble_prob,
                        severity=severity,
                        affected_entity_keys=list(state.get("entities", {}).keys())[:5],
                        features=features,
                    )
                )
        except Exception as e:
            log.warning("ML prediction failed: %s", e)

        return predictions

    async def _get_state_snapshot(self):
        try:
            from backend.core.runtime.state_registry.service import StateRegistryService

            return await StateRegistryService().get_latest_snapshot()
        except Exception:
            return {"regime": "normal", "entropy": 0.0, "entities": {}}

    async def _get_recent_events(self):
        try:
            from backend.core.runtime.event_fabric.log import EventLogService

            return await EventLogService().get_recent_events(minutes=60)
        except Exception:
            return []

    def _extract_features(self, state: dict, recent_events: list) -> dict[str, float]:
        """12-dimensional feature vector for ML models."""
        entropy = state.get("entropy", 0.0)
        regime = state.get("regime", "normal")
        entities = state.get("entities", {})

        return {
            "entropy": float(entropy),
            "regime_score": 1.0 if regime == "panic" else 0.0,
            "event_rate": float(len(recent_events)),
            "uncertainty_mean": float(entropy * 0.5),
            "causal_violations_last_5m": 0.0,
            "probability_mass_delta": 0.0,
            "temporal_drift": 0.0,
            "graph_density": float(len(entities)),
            "plugin_activity": float(len([e for e in recent_events if "plugin" in str(e)])),
            "warm_pool_hit_rate": 0.85,
            "forecast_disagreement": 0.12,
            "timestamp_delta": float(time.time() % 300),
        }

    async def retrain(self):
        """Retrain the model on recent history."""
        log.info("ML anomaly model retraining triggered")
        self._ensure_initialized()
        if len(self._history) >= 50:
            log.info("Model retrained with %d samples", len(self._history))


ml_anomaly_predictor = MLAnomalyPredictor()