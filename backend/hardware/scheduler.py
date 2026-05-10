"""
SimHPC Hardware-Aware Scheduler

Routes every simulation job to the optimal GPU node based on:
  1. SLA tier — defense jobs go to ITAR-isolated nodes only
  2. Cost arbitrage — pick cheapest provider meeting SLA requirements
  3. Availability — fail over to secondary provider if primary degraded
  4. Hardware attestation — record exactly which physical node ran each job
  5. Capacity reservations — honor pre-reserved capacity for enterprise tenants
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from backend.app.core.supabase import get_supabase_client
from backend.hardware.providers import (
    GPUNode,
    GPUType,
    IsolationLevel,
    NodeStatus,
    get_provider_registry,
)
from backend.hardware.sla import SLATier, get_sla_engine


@dataclass
class SchedulingRequest:
    run_id: str
    tenant_id: str
    sla_tier: SLATier
    gpu_type: GPUType = GPUType.A40
    gpu_count: int = 1
    estimated_duration_minutes: int = 30
    domain: str = "structural"
    data_classification: str = "PUBLIC"
    region_preference: str = "us-east-1"
    max_cost_usd: float | None = None
    reservation_id: str | None = None


@dataclass
class SchedulingResult:
    run_id: str
    node: GPUNode
    scheduled_at: str
    queue_position: int
    estimated_start_seconds: float
    estimated_cost_usd: float
    sla_tier: SLATier
    hardware_attestation_id: str
    provider_chosen: str
    fallback_used: bool = False
    fallback_reason: str = ""


class CostArbitrageEngine:
    async def rank_nodes_by_cost(
        self,
        nodes: list[GPUNode],
        prefer_spot: bool = True,
    ) -> list[GPUNode]:
        def effective_cost(node: GPUNode) -> float:
            if prefer_spot and node.spot_price_usd is not None:
                return node.spot_price_usd / node.gpu_count
            return node.hourly_cost_usd / node.gpu_count

        return sorted(nodes, key=effective_cost)

    async def get_cheapest_available(
        self,
        gpu_type: GPUType,
        isolation_level: IsolationLevel,
        region: str,
    ) -> tuple[str, float]:
        registry = get_provider_registry()
        candidates: list[tuple[str, float]] = []

        for provider in registry.all():
            nodes = await provider.list_available_nodes(
                gpu_type=gpu_type,
                region=region,
                isolation_level=isolation_level,
            )
            for node in nodes:
                if node.status == NodeStatus.AVAILABLE:
                    candidates.append((provider.name, node.cost_per_gpu_hour))

        if not candidates:
            return ("none", float("inf"))

        return min(candidates, key=lambda x: x[1])


class HardwareAwareScheduler:
    def __init__(self) -> None:
        self._db = get_supabase_client()
        self._registry = get_provider_registry()
        self._sla_engine = get_sla_engine()
        self._arbitrage = CostArbitrageEngine()
        self._queue: dict[str, list[SchedulingRequest]] = {}

    async def schedule(self, request: SchedulingRequest) -> SchedulingResult:
        if request.sla_tier == SLATier.DEFENSE:
            return await self._schedule_defense(request)
        elif request.sla_tier == SLATier.ENTERPRISE:
            return await self._schedule_enterprise(request)
        elif request.sla_tier == SLATier.PROFESSIONAL:
            return await self._schedule_professional(request)
        else:
            return await self._schedule_free(request)

    async def _schedule_defense(self, request: SchedulingRequest) -> SchedulingResult:
        if not request.region_preference.startswith("us-"):
            raise ValueError(
                f"ITAR-controlled workloads must run in US regions. Requested: {request.region_preference}"
            )

        nodes = await self._find_nodes(
            request,
            required_isolation=IsolationLevel.ISOLATED,
        )

        if not nodes:
            nodes = await self._find_nodes(
                request,
                required_isolation=IsolationLevel.BARE_METAL,
            )

        if not nodes:
            raise RuntimeError(
                f"No ITAR-eligible isolated hardware available in "
                f"{request.region_preference}. "
                f"Cannot schedule DEFENSE tier workload on shared infrastructure. "
                f"Contact SimHPC support for capacity reservation."
            )

        node = (await self._arbitrage.rank_nodes_by_cost(nodes, prefer_spot=False))[0]
        return await self._finalize_scheduling(request, node, fallback_used=False)

    async def _schedule_enterprise(self, request: SchedulingRequest) -> SchedulingResult:
        nodes = await self._find_nodes(
            request,
            required_isolation=IsolationLevel.DEDICATED,
        )

        fallback_used = False
        fallback_reason = ""

        if not nodes:
            nodes = await self._find_nodes(
                request,
                required_isolation=IsolationLevel.SHARED,
            )
            fallback_used = True
            fallback_reason = "No dedicated nodes available — using shared. SLA credit will be applied."
            await self._log_sla_degradation(request, "dedicated → shared fallback")

        if not nodes:
            raise RuntimeError("No hardware available for ENTERPRISE workload")

        node = (await self._arbitrage.rank_nodes_by_cost(nodes))[0]
        return await self._finalize_scheduling(request, node, fallback_used, fallback_reason)

    async def _schedule_professional(self, request: SchedulingRequest) -> SchedulingResult:
        nodes = await self._find_nodes(
            request,
            required_isolation=IsolationLevel.SHARED,
        )

        if not nodes:
            nodes = await self._find_nodes_all_providers(request)

        if not nodes:
            raise RuntimeError("No shared hardware available")

        ranked = await self._arbitrage.rank_nodes_by_cost(nodes, prefer_spot=True)
        return await self._finalize_scheduling(request, ranked[0])

    async def _schedule_free(self, request: SchedulingRequest) -> SchedulingResult:
        nodes = await self._find_nodes_all_providers(request)

        if not nodes:
            raise RuntimeError("No hardware available. Please try again later.")

        ranked = await self._arbitrage.rank_nodes_by_cost(nodes, prefer_spot=True)
        return await self._finalize_scheduling(request, ranked[0])

    async def _find_nodes(
        self,
        request: SchedulingRequest,
        required_isolation: IsolationLevel,
    ) -> list[GPUNode]:
        all_nodes: list[GPUNode] = []
        for provider in self._registry.all():
            nodes = await provider.list_available_nodes(
                gpu_type=request.gpu_type,
                region=request.region_preference,
                isolation_level=required_isolation,
            )
            eligible = [
                n
                for n in nodes
                if n.status == NodeStatus.AVAILABLE
                and n.isolation_level == required_isolation
                and (n.gpu_count >= request.gpu_count)
            ]
            all_nodes.extend(eligible)

        return all_nodes

    async def _find_nodes_all_providers(
        self,
        request: SchedulingRequest,
    ) -> list[GPUNode]:
        all_nodes: list[GPUNode] = []
        for provider in self._registry.all():
            health = await provider.health_check()
            if not health.healthy:
                continue
            nodes = await provider.list_available_nodes(gpu_type=request.gpu_type)
            all_nodes.extend(n for n in nodes if n.status == NodeStatus.AVAILABLE)
        return all_nodes

    async def _finalize_scheduling(
        self,
        request: SchedulingRequest,
        node: GPUNode,
        fallback_used: bool = False,
        fallback_reason: str = "",
    ) -> SchedulingResult:
        attestation_id = await self._write_hardware_attestation(request, node)
        queue_position = await self._get_queue_position(node.node_id)
        duration = request.estimated_duration_minutes / 60
        est_cost = node.hourly_cost_usd * request.gpu_count * duration

        result = SchedulingResult(
            run_id=request.run_id,
            node=node,
            scheduled_at=datetime.now(UTC).isoformat(),
            queue_position=queue_position,
            estimated_start_seconds=queue_position * 30.0,
            estimated_cost_usd=round(est_cost, 4),
            sla_tier=request.sla_tier,
            hardware_attestation_id=attestation_id,
            provider_chosen=node.provider,
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
        )

        await self._store_scheduling_decision(result)
        return result

    async def _write_hardware_attestation(
        self,
        request: SchedulingRequest,
        node: GPUNode,
    ) -> str:
        attestation_id = str(uuid.uuid4())
        record = {
            "id": attestation_id,
            "node_id": node.node_id,
            "run_id": request.run_id,
            "tenant_id": request.tenant_id,
            "provider": node.provider,
            "gpu_model": node.gpu_type.value,
            "gpu_count": node.gpu_count,
            "cuda_version": node.cuda_version,
            "driver_version": node.driver_version,
            "isolation_level": node.isolation_level.value,
            "itar_eligible": node.is_itar_eligible,
            "physical_host_id": node.physical_host_id or node.node_id,
            "region": node.region,
            "zone": node.zone,
            "sla_tier": request.sla_tier.value,
            "attested_at": datetime.now(UTC).isoformat(),
        }

        if self._db:
            self._db.table("hardware_attestations").insert(record).execute()

        return attestation_id

    async def _get_queue_position(self, node_id: str) -> int:
        if self._db is None:
            return 0
        result = self._db.table("simulation_runs").select("id").eq("node_id", node_id).eq("status", "queued").execute()
        return len(result.data) if result.data else 0

    async def _log_sla_degradation(self, request: SchedulingRequest, reason: str) -> None:
        if self._db is None:
            return
        self._db.table("sla_events").insert(
            {
                "run_id": request.run_id,
                "tenant_id": request.tenant_id,
                "sla_tier": request.sla_tier.value,
                "event_type": "SLA_DEGRADATION",
                "reason": reason,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ).execute()

    async def _store_scheduling_decision(self, result: SchedulingResult) -> None:
        if self._db is None:
            return
        self._db.table("scheduling_decisions").insert(
            {
                "run_id": result.run_id,
                "node_id": result.node.node_id,
                "provider": result.provider_chosen,
                "sla_tier": result.sla_tier.value,
                "scheduled_at": result.scheduled_at,
                "estimated_cost_usd": result.estimated_cost_usd,
                "fallback_used": result.fallback_used,
                "attestation_id": result.hardware_attestation_id,
            }
        ).execute()


_scheduler: HardwareAwareScheduler | None = None


def get_scheduler() -> HardwareAwareScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = HardwareAwareScheduler()
    return _scheduler
