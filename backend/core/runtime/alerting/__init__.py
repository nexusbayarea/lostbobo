"""Real-time Alerting System — operational nervous system."""

from __future__ import annotations

from backend.core.runtime.alerting.engine import (
    Alert,
    AlertFatigueGuard,
    RealTimeAlertingSystem,
    get_alerting_system,
)
from backend.core.runtime.alerting.escalation import (
    AlertEscalationManager,
    EscalationPolicy,
    get_escalation_manager,
)

__all__ = [
    "Alert",
    "AlertEscalationManager",
    "AlertFatigueGuard",
    "EscalationPolicy",
    "RealTimeAlertingSystem",
    "get_alerting_system",
    "get_escalation_manager",
]
