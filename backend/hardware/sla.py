"""
SimHPC SLA Contract Engine

Defines, tracks, and enforces guaranteed SLAs per tenant tier.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from backend.app.core.supabase import get_supabase_client


class SLATier(str, Enum):
    FREE = "free"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    DEFENSE = "defense"
    CUSTOM = "custom"


@dataclass
class SLAContract:
    tier: SLATier
    uptime_target_pct: float
    max_monthly_downtime_minutes: float
    queue_time_p95_seconds: float
    queue_time_p99_seconds: float
    max_queue_depth: int
    simulation_timeout_minutes: int
    result_delivery_sla_minutes: int
    isolation_level: str
    itar_eligible: bool
    support_response_hours: float
    support_tier: str
    credit_rate_per_hour_breach: float
    max_monthly_credit_pct: float
    base_monthly_usd: float
    per_simulation_usd: float
    dedicated_node_hourly_usd: float | None

    def monthly_credit_cap_usd(self, monthly_invoice: float) -> float:
        return monthly_invoice * (self.max_monthly_credit_pct / 100)


SLA_DEFINITIONS: dict[SLATier, SLAContract] = {
    SLATier.FREE: SLAContract(
        tier=SLATier.FREE,
        uptime_target_pct=95.0,
        max_monthly_downtime_minutes=36 * 60,
        queue_time_p95_seconds=300,
        queue_time_p99_seconds=600,
        max_queue_depth=100,
        simulation_timeout_minutes=30,
        result_delivery_sla_minutes=60,
        isolation_level="shared",
        itar_eligible=False,
        support_response_hours=168,
        support_tier="community",
        credit_rate_per_hour_breach=0.0,
        max_monthly_credit_pct=0.0,
        base_monthly_usd=0.0,
        per_simulation_usd=0.0,
        dedicated_node_hourly_usd=None,
    ),
    SLATier.PROFESSIONAL: SLAContract(
        tier=SLATier.PROFESSIONAL,
        uptime_target_pct=99.5,
        max_monthly_downtime_minutes=3.6 * 60,
        queue_time_p95_seconds=30,
        queue_time_p99_seconds=60,
        max_queue_depth=20,
        simulation_timeout_minutes=120,
        result_delivery_sla_minutes=10,
        isolation_level="shared",
        itar_eligible=False,
        support_response_hours=8,
        support_tier="business",
        credit_rate_per_hour_breach=5.0,
        max_monthly_credit_pct=25.0,
        base_monthly_usd=299.0,
        per_simulation_usd=2.50,
        dedicated_node_hourly_usd=None,
    ),
    SLATier.ENTERPRISE: SLAContract(
        tier=SLATier.ENTERPRISE,
        uptime_target_pct=99.9,
        max_monthly_downtime_minutes=43.8,
        queue_time_p95_seconds=10,
        queue_time_p99_seconds=20,
        max_queue_depth=5,
        simulation_timeout_minutes=480,
        result_delivery_sla_minutes=5,
        isolation_level="dedicated",
        itar_eligible=False,
        support_response_hours=2,
        support_tier="enterprise",
        credit_rate_per_hour_breach=25.0,
        max_monthly_credit_pct=30.0,
        base_monthly_usd=2499.0,
        per_simulation_usd=0.0,
        dedicated_node_hourly_usd=3.20,
    ),
    SLATier.DEFENSE: SLAContract(
        tier=SLATier.DEFENSE,
        uptime_target_pct=99.95,
        max_monthly_downtime_minutes=21.9,
        queue_time_p95_seconds=5,
        queue_time_p99_seconds=10,
        max_queue_depth=2,
        simulation_timeout_minutes=1440,
        result_delivery_sla_minutes=2,
        isolation_level="isolated",
        itar_eligible=True,
        support_response_hours=0.5,
        support_tier="24x7",
        credit_rate_per_hour_breach=100.0,
        max_monthly_credit_pct=50.0,
        base_monthly_usd=9999.0,
        per_simulation_usd=0.0,
        dedicated_node_hourly_usd=None,
    ),
    SLATier.CUSTOM: SLAContract(
        tier=SLATier.CUSTOM,
        uptime_target_pct=99.99,
        max_monthly_downtime_minutes=4.38,
        queue_time_p95_seconds=2,
        queue_time_p99_seconds=5,
        max_queue_depth=1,
        simulation_timeout_minutes=2880,
        result_delivery_sla_minutes=1,
        isolation_level="bare_metal",
        itar_eligible=True,
        support_response_hours=0.25,
        support_tier="dedicated_csm",
        credit_rate_per_hour_breach=500.0,
        max_monthly_credit_pct=100.0,
        base_monthly_usd=0.0,
        per_simulation_usd=0.0,
        dedicated_node_hourly_usd=None,
    ),
}


class SLABreachType(str, Enum):
    UPTIME_VIOLATION = "UPTIME_VIOLATION"
    QUEUE_TIME_P95 = "QUEUE_TIME_P95"
    QUEUE_TIME_P99 = "QUEUE_TIME_P99"
    RESULT_DELIVERY_LATE = "RESULT_DELIVERY_LATE"
    SIMULATION_TIMEOUT = "SIMULATION_TIMEOUT"
    SUPPORT_RESPONSE_LATE = "SUPPORT_RESPONSE_LATE"
    HARDWARE_ISOLATION_FAIL = "HARDWARE_ISOLATION_FAIL"


@dataclass
class SLABreach:
    breach_id: str
    tenant_id: str
    tier: SLATier
    breach_type: SLABreachType
    detected_at: str
    resolved_at: str | None
    duration_minutes: float
    target_value: float
    actual_value: float
    credit_usd: float
    notified: bool = False
    run_id: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "breach_id": self.breach_id,
            "tenant_id": self.tenant_id,
            "tier": self.tier.value,
            "breach_type": self.breach_type.value,
            "detected_at": self.detected_at,
            "resolved_at": self.resolved_at,
            "duration_minutes": self.duration_minutes,
            "target_value": self.target_value,
            "actual_value": self.actual_value,
            "credit_usd": self.credit_usd,
            "notified": self.notified,
            "run_id": self.run_id,
            "details": self.details,
        }


class SLAContractEngine:
    def __init__(self) -> None:
        self._db = get_supabase_client()

    def get_contract(self, tier: SLATier) -> SLAContract:
        return SLA_DEFINITIONS[tier]

    def get_contract_for_tenant(self, tenant_sla_tier: str) -> SLAContract:
        try:
            return SLA_DEFINITIONS[SLATier(tenant_sla_tier)]
        except (ValueError, KeyError):
            return SLA_DEFINITIONS[SLATier.FREE]

    async def check_queue_time_breach(
        self,
        tenant_id: str,
        tier: SLATier,
        actual_queue_seconds: float,
        run_id: str | None = None,
    ) -> SLABreach | None:
        contract = self.get_contract(tier)
        if actual_queue_seconds <= contract.queue_time_p95_seconds:
            return None

        duration_overage = actual_queue_seconds - contract.queue_time_p95_seconds
        credit = self._calculate_credit(contract, duration_minutes=duration_overage / 60)

        breach = SLABreach(
            breach_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            tier=tier,
            breach_type=SLABreachType.QUEUE_TIME_P95,
            detected_at=datetime.now(UTC).isoformat(),
            resolved_at=datetime.now(UTC).isoformat(),
            duration_minutes=duration_overage / 60,
            target_value=contract.queue_time_p95_seconds,
            actual_value=actual_queue_seconds,
            credit_usd=credit,
            run_id=run_id,
        )
        await self._store_breach(breach)
        return breach

    async def check_uptime_breach(
        self,
        tenant_id: str,
        tier: SLATier,
        downtime_minutes: float,
    ) -> SLABreach | None:
        contract = self.get_contract(tier)
        if downtime_minutes <= contract.max_monthly_downtime_minutes:
            return None

        overage = downtime_minutes - contract.max_monthly_downtime_minutes
        credit = self._calculate_credit(contract, duration_minutes=overage)

        breach = SLABreach(
            breach_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            tier=tier,
            breach_type=SLABreachType.UPTIME_VIOLATION,
            detected_at=datetime.now(UTC).isoformat(),
            resolved_at=None,
            duration_minutes=overage,
            target_value=contract.max_monthly_downtime_minutes,
            actual_value=downtime_minutes,
            credit_usd=credit,
        )
        await self._store_breach(breach)
        return breach

    async def check_hardware_isolation_breach(
        self,
        tenant_id: str,
        tier: SLATier,
        actual_isolation: str,
        run_id: str | None = None,
    ) -> SLABreach | None:
        contract = self.get_contract(tier)
        isolation_rank = {"shared": 0, "dedicated": 1, "isolated": 2, "bare_metal": 3}
        required_rank = isolation_rank.get(contract.isolation_level, 0)
        actual_rank = isolation_rank.get(actual_isolation, 0)

        if actual_rank >= required_rank:
            return None

        credit = self._calculate_credit(contract, duration_minutes=60.0)

        breach = SLABreach(
            breach_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            tier=tier,
            breach_type=SLABreachType.HARDWARE_ISOLATION_FAIL,
            detected_at=datetime.now(UTC).isoformat(),
            resolved_at=datetime.now(UTC).isoformat(),
            duration_minutes=0.0,
            target_value=float(required_rank),
            actual_value=float(actual_rank),
            credit_usd=credit,
            run_id=run_id,
            details={
                "required_isolation": contract.isolation_level,
                "actual_isolation": actual_isolation,
                "itar_eligible_required": contract.itar_eligible,
            },
        )
        await self._store_breach(breach)
        return breach

    async def get_tenant_breaches(
        self,
        tenant_id: str,
        month: str | None = None,
    ) -> list[dict[str, Any]]:
        if self._db is None:
            return []
        query = self._db.table("sla_breaches").select("*").eq("tenant_id", tenant_id).order("detected_at", desc=True)
        if month:
            query = query.gte("detected_at", f"{month}-01T00:00:00Z")
        result = query.execute()
        return result.data or []

    async def calculate_monthly_credits(
        self,
        tenant_id: str,
        month: str,
        monthly_invoice_usd: float,
    ) -> dict[str, Any]:
        breaches = await self.get_tenant_breaches(tenant_id, month)
        total_credit = sum(b.get("credit_usd", 0) for b in breaches)

        tier_str = breaches[0].get("tier", "free") if breaches else "free"
        contract = self.get_contract_for_tenant(tier_str)
        cap = contract.monthly_credit_cap_usd(monthly_invoice_usd)
        capped_credit = min(total_credit, cap)

        return {
            "tenant_id": tenant_id,
            "month": month,
            "breach_count": len(breaches),
            "gross_credit_usd": round(total_credit, 2),
            "credit_cap_usd": round(cap, 2),
            "net_credit_usd": round(capped_credit, 2),
            "breaches_by_type": self._group_by_type(breaches),
            "invoice_after_credit": round(monthly_invoice_usd - capped_credit, 2),
        }

    def _calculate_credit(
        self,
        contract: SLAContract,
        duration_minutes: float,
    ) -> float:
        hours = duration_minutes / 60
        return round(hours * contract.credit_rate_per_hour_breach, 2)

    def _group_by_type(self, breaches: list[dict]) -> dict[str, int]:
        out: dict[str, int] = {}
        for b in breaches:
            t = b.get("breach_type", "unknown")
            out[t] = out.get(t, 0) + 1
        return out

    async def _store_breach(self, breach: SLABreach) -> None:
        if self._db is None:
            return
        self._db.table("sla_breaches").insert(breach.to_dict()).execute()


_engine: SLAContractEngine | None = None


def get_sla_engine() -> SLAContractEngine:
    global _engine
    if _engine is None:
        _engine = SLAContractEngine()
    return _engine
