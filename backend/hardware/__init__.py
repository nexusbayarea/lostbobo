"""Hardware Moat Layer — SLA-enforced compute governance."""

from __future__ import annotations

from backend.hardware.hardware import router
from backend.hardware.providers import (
    GPUNode,
    GPUType,
    IsolationLevel,
    NodeStatus,
    ProviderHealth,
    ProviderInterface,
    get_provider_registry,
)
from backend.hardware.reservations import (
    CapacityReservation,
    CapacityReservationSystem,
    ReservationType,
    get_reservation_system,
)
from backend.hardware.scheduler import (
    HardwareAwareScheduler,
    SchedulingRequest,
    SchedulingResult,
    get_scheduler,
)
from backend.hardware.sla import (
    SLA_DEFINITIONS,
    SLABreach,
    SLABreachType,
    SLAContract,
    SLAContractEngine,
    SLATier,
    get_sla_engine,
)

__all__ = [
    "router",
    "GPUType",
    "IsolationLevel",
    "NodeStatus",
    "ProviderHealth",
    "ProviderInterface",
    "GPUNode",
    "get_provider_registry",
    "CapacityReservation",
    "CapacityReservationSystem",
    "ReservationType",
    "get_reservation_system",
    "HardwareAwareScheduler",
    "SchedulingRequest",
    "SchedulingResult",
    "get_scheduler",
    "SLABreach",
    "SLABreachType",
    "SLAContract",
    "SLAContractEngine",
    "SLA_DEFINITIONS",
    "SLATier",
    "get_sla_engine",
]
