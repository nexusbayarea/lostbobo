"""Alert escalation policies with automatic triggering and timer management."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class EscalationPolicy:
    severity: str
    max_ack_time_minutes: int
    max_resolve_time_minutes: int
    escalation_chain: list[str] = field(default_factory=list)
    notify_channels: list[str] = field(default_factory=list)


class AlertEscalationManager:
    _instance: AlertEscalationManager | None = None
    _policies: dict[str, EscalationPolicy] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._policies = {
            "CRITICAL": EscalationPolicy(
                severity="CRITICAL",
                max_ack_time_minutes=5,
                max_resolve_time_minutes=30,
                escalation_chain=["oncall", "engineering", "cto"],
                notify_channels=["pagerduty", "slack"],
            ),
            "WARNING": EscalationPolicy(
                severity="WARNING",
                max_ack_time_minutes=15,
                max_resolve_time_minutes=60,
                escalation_chain=["oncall", "engineering"],
                notify_channels=["slack"],
            ),
            "INFO": EscalationPolicy(
                severity="INFO",
                max_ack_time_minutes=60,
                max_resolve_time_minutes=240,
                escalation_chain=["engineering"],
                notify_channels=["slack"],
            ),
        }

    @classmethod
    def manager(cls) -> AlertEscalationManager:
        return cls()

    async def check_escalation(self, alert: Any) -> bool:
        self._ensure_initialized()
        if alert.status in ("RESOLVED", "ESCALATED"):
            return False

        policy = self._policies.get(alert.severity)
        if not policy:
            return False

        now = datetime.now(UTC)
        created_at = getattr(alert, "acknowledged_at", None) or now

        try:
            if hasattr(alert, "created_at") and alert.acknowledged_at is None:
                created_at = alert.created_at
            elif alert.acknowledged_at:
                created_at = alert.acknowledged_at
        except Exception:
            created_at = now

        if getattr(alert, "acknowledged_at", None) is None:
            time_since_creation = (now - created_at).total_seconds() / 60
            if time_since_creation > policy.max_ack_time_minutes:
                return await self._escalate(alert, policy, 1)
        elif getattr(alert, "resolved_at", None) is None:
            ack_time = getattr(alert, "acknowledged_at", now)
            time_since_ack = (now - ack_time).total_seconds() / 60
            if time_since_ack > policy.max_resolve_time_minutes:
                return await self._escalate(alert, policy, 2)

        return False

    async def _escalate(self, alert: Any, policy: EscalationPolicy, level: int) -> bool:
        try:
            from backend.core.runtime.alerting.engine import RealTimeAlertingSystem

            alerting = RealTimeAlertingSystem.alerts()
            alert.status = "ESCALATED"
            alerting._store_alert(alert)
        except Exception:
            pass

        next_contact = policy.escalation_chain[min(level, len(policy.escalation_chain) - 1)]

        try:
            from backend.core.services.observability_service import observability

            observability().increment("alerts_escalated_total")
        except Exception:
            pass

        try:
            from backend.core.runtime.event_fabric.log import EventLogService
            from backend.core.runtime.event_fabric.schema import SimHPCEvent

            await EventLogService.event_log().publish(
                SimHPCEvent(
                    event_type="alert.escalated",
                    source_plugin="kernel",
                    confidence=getattr(alert, "confidence", 0.0),
                    payload={
                        "alert_id": alert.id,
                        "escalation_level": level,
                        "next_contact": next_contact,
                        "policy": policy.severity,
                    },
                )
            )
        except Exception:
            pass

        try:
            asyncio.create_task(self._notify_escalated(alert, next_contact))
        except Exception:
            pass

        return True

    async def _notify_escalated(self, alert: Any, next_contact: str) -> None:
        try:
            from backend.core.infisical import get_secret

            webhook = get_secret("SLACK_WEBHOOK_URL", "")
            if not webhook:
                return

            import aiohttp

            payload = {
                "text": f"[ESCALATED] {getattr(alert, 'title', 'Alert')}",
                "attachments": [
                    {
                        "color": "#ff0000",
                        "fields": [
                            {"title": "Contact", "value": next_contact, "short": True},
                            {"title": "Entity", "value": getattr(alert, "entity_id", "unknown"), "short": True},
                        ],
                    }
                ],
            }
            async with aiohttp.ClientSession() as session:
                await session.post(webhook, json=payload)
        except Exception as e:
            logger.warning(f"Escalation notification failed: {e}")

    def get_policy(self, severity: str) -> EscalationPolicy | None:
        self._ensure_initialized()
        return self._policies.get(severity)

    def update_policy(self, policy: EscalationPolicy) -> None:
        self._ensure_initialized()
        self._policies[policy.severity] = policy


def get_escalation_manager() -> AlertEscalationManager:
    return AlertEscalationManager.manager()
