"""
SimHPC Capacity Reservation System

Allows enterprise/defense tenants to pre-reserve dedicated GPU-hours.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from backend.app.core.supabase import get_supabase_client
from backend.hardware.providers import GPUType, IsolationLevel


class ReservationType(str, Enum):
    SPOT_POOL = "spot_pool"
    RESERVED_1M = "reserved_1m"
    RESERVED_3M = "reserved_3m"
    RESERVED_1Y = "reserved_1y"
    DEDICATED = "dedicated"


RESERVATION_DISCOUNTS: dict[ReservationType, float] = {
    ReservationType.SPOT_POOL: 0.00,
    ReservationType.RESERVED_1M: 0.15,
    ReservationType.RESERVED_3M: 0.25,
    ReservationType.RESERVED_1Y: 0.40,
    ReservationType.DEDICATED: 0.35,
}

WHOLESALE_COST_MULTIPLIER = 0.60


@dataclass
class CapacityReservation:
    reservation_id: str
    tenant_id: str
    provider: str
    gpu_type: GPUType
    gpu_count: int
    isolation_level: IsolationLevel
    reservation_type: ReservationType
    region: str
    start_date: str
    end_date: str
    gpu_hours_reserved: float
    gpu_hours_used: float
    retail_hourly_rate: float
    wholesale_hourly_rate: float
    discount_applied: float
    status: str = "ACTIVE"
    node_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def gpu_hours_remaining(self) -> float:
        return max(0.0, self.gpu_hours_reserved - self.gpu_hours_used)

    @property
    def utilization_pct(self) -> float:
        if self.gpu_hours_reserved == 0:
            return 0.0
        return (self.gpu_hours_used / self.gpu_hours_reserved) * 100

    @property
    def simhpc_margin_per_hour(self) -> float:
        return self.retail_hourly_rate - self.wholesale_hourly_rate

    def to_dict(self) -> dict[str, Any]:
        return {
            "reservation_id": self.reservation_id,
            "tenant_id": self.tenant_id,
            "provider": self.provider,
            "gpu_type": self.gpu_type.value,
            "gpu_count": self.gpu_count,
            "isolation_level": self.isolation_level.value,
            "reservation_type": self.reservation_type.value,
            "region": self.region,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "gpu_hours_reserved": self.gpu_hours_reserved,
            "gpu_hours_used": self.gpu_hours_used,
            "gpu_hours_remaining": self.gpu_hours_remaining,
            "utilization_pct": round(self.utilization_pct, 2),
            "retail_hourly_rate": self.retail_hourly_rate,
            "wholesale_hourly_rate": self.wholesale_hourly_rate,
            "discount_applied": self.discount_applied,
            "simhpc_margin_per_hour": round(self.simhpc_margin_per_hour, 4),
            "status": self.status,
            "node_id": self.node_id,
        }


class CapacityReservationSystem:
    def __init__(self) -> None:
        self._db = get_supabase_client()

    async def create_reservation(
        self,
        tenant_id: str,
        provider: str,
        gpu_type: GPUType,
        gpu_count: int,
        isolation_level: IsolationLevel,
        reservation_type: ReservationType,
        region: str,
        duration_days: int,
        retail_on_demand_hourly: float,
    ) -> CapacityReservation:
        discount = RESERVATION_DISCOUNTS[reservation_type]
        retail_rate = retail_on_demand_hourly * (1 - discount)
        wholesale_rate = retail_on_demand_hourly * WHOLESALE_COST_MULTIPLIER
        total_hours = duration_days * 24 * gpu_count

        now = datetime.now(UTC)
        reservation = CapacityReservation(
            reservation_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            provider=provider,
            gpu_type=gpu_type,
            gpu_count=gpu_count,
            isolation_level=isolation_level,
            reservation_type=reservation_type,
            region=region,
            start_date=now.isoformat(),
            end_date=now.replace(day=now.day + duration_days).isoformat(),
            gpu_hours_reserved=total_hours,
            gpu_hours_used=0.0,
            retail_hourly_rate=round(retail_rate, 4),
            wholesale_hourly_rate=round(wholesale_rate, 4),
            discount_applied=discount,
        )

        if self._db:
            self._db.table("capacity_reservations").insert(reservation.to_dict()).execute()

        return reservation

    async def consume_hours(
        self,
        reservation_id: str,
        hours_used: float,
    ) -> bool:
        if self._db is None:
            return True
        result = (
            self._db.table("capacity_reservations")
            .select("gpu_hours_used, gpu_hours_reserved")
            .eq("reservation_id", reservation_id)
            .single()
            .execute()
        )

        if not result.data:
            return False

        new_used = result.data["gpu_hours_used"] + hours_used
        self._db.table("capacity_reservations").update({"gpu_hours_used": new_used}).eq(
            "reservation_id", reservation_id
        ).execute()
        return True

    async def get_active_reservations(self, tenant_id: str) -> list[dict[str, Any]]:
        if self._db is None:
            return []
        result = (
            self._db.table("capacity_reservations")
            .select("*")
            .eq("tenant_id", tenant_id)
            .eq("status", "ACTIVE")
            .execute()
        )
        return result.data or []

    async def get_platform_utilization(self) -> dict[str, Any]:
        if self._db is None:
            return {}
        result = self._db.table("capacity_reservations").select("*").eq("status", "ACTIVE").execute()
        reservations = result.data or []

        total_reserved = sum(r.get("gpu_hours_reserved", 0) for r in reservations)
        total_used = sum(r.get("gpu_hours_used", 0) for r in reservations)
        total_margin = sum(r.get("simhpc_margin_per_hour", 0) * r.get("gpu_count", 1) for r in reservations)

        return {
            "active_reservations": len(reservations),
            "total_gpu_hours_reserved": round(total_reserved, 1),
            "total_gpu_hours_used": round(total_used, 1),
            "platform_utilization_pct": round((total_used / total_reserved * 100) if total_reserved else 0, 2),
            "estimated_monthly_margin_usd": round(total_margin * 730, 2),
            "by_provider": self._group_by(reservations, "provider"),
            "by_gpu_type": self._group_by(reservations, "gpu_type"),
        }

    def _group_by(self, items: list[dict], key: str) -> dict[str, int]:
        out: dict[str, int] = {}
        for item in items:
            v = item.get(key, "unknown")
            out[v] = out.get(v, 0) + 1
        return out


_reservation_system: CapacityReservationSystem | None = None


def get_reservation_system() -> CapacityReservationSystem:
    global _reservation_system
    if _reservation_system is None:
        _reservation_system = CapacityReservationSystem()
    return _reservation_system
