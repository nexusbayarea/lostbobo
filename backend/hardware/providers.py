"""
SimHPC Hardware Provider Abstraction Layer

Decouples SimHPC from any single GPU cloud provider.
Today: RunPod A40s.
Tomorrow: CoreWeave H100s, AWS p4d.24xlarge, Azure NDv4, on-prem.
"""

from __future__ import annotations

import asyncio
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class GPUType(str, Enum):
    A40 = "NVIDIA_A40"
    A100_40GB = "NVIDIA_A100_40GB"
    A100_80GB = "NVIDIA_A100_80GB"
    H100_80GB = "NVIDIA_H100_80GB"
    H100_NVL = "NVIDIA_H100_NVL"
    RTX_4090 = "NVIDIA_RTX_4090"
    L40S = "NVIDIA_L40S"


class NodeStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    PROVISIONING = "PROVISIONING"
    RUNNING = "RUNNING"
    IDLE = "IDLE"
    TERMINATING = "TERMINATING"
    TERMINATED = "TERMINATED"
    DEGRADED = "DEGRADED"
    RESERVED = "RESERVED"


class IsolationLevel(str, Enum):
    SHARED = "SHARED"
    DEDICATED = "DEDICATED"
    ISOLATED = "ISOLATED"
    BARE_METAL = "BARE_METAL"


@dataclass
class GPUNode:
    node_id: str
    provider: str
    gpu_type: GPUType
    gpu_count: int
    vram_gb: int
    vcpus: int
    ram_gb: int
    region: str
    zone: str
    status: NodeStatus
    isolation_level: IsolationLevel
    hourly_cost_usd: float
    spot_price_usd: float | None
    provisioned_at: str | None
    last_heartbeat: str | None
    tenant_id: str | None
    compliance_certifications: list[str] = field(default_factory=list)
    physical_host_id: str = ""
    cuda_version: str = ""
    driver_version: str = ""
    network_bandwidth_gbps: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_itar_eligible(self) -> bool:
        return (
            self.isolation_level in (IsolationLevel.ISOLATED, IsolationLevel.BARE_METAL)
            and self.region.startswith("us-")
            and ("SOC2" in self.compliance_certifications or "ITAR" in self.compliance_certifications)
        )

    @property
    def cost_per_gpu_hour(self) -> float:
        return self.hourly_cost_usd / max(self.gpu_count, 1)


@dataclass
class ProvisionRequest:
    gpu_type: GPUType
    gpu_count: int = 1
    isolation_level: IsolationLevel = IsolationLevel.SHARED
    region: str = "us-east-1"
    tenant_id: str | None = None
    max_hourly_cost_usd: float = 10.0
    require_compliance: list[str] = field(default_factory=list)
    preferred_provider: str | None = None
    spot_ok: bool = True
    reservation_id: str | None = None


@dataclass
class ProviderHealth:
    provider: str
    healthy: bool
    latency_ms: float
    available_nodes: int
    spot_price_usd: float | None
    last_checked: str
    error: str | None = None


class ProviderInterface(ABC):
    @abstractmethod
    async def list_available_nodes(
        self,
        gpu_type: GPUType | None = None,
        region: str | None = None,
        isolation_level: IsolationLevel | None = None,
    ) -> list[GPUNode]: ...

    @abstractmethod
    async def provision_node(self, request: ProvisionRequest) -> GPUNode: ...

    @abstractmethod
    async def terminate_node(self, node_id: str) -> bool: ...

    @abstractmethod
    async def get_node_telemetry(self, node_id: str) -> dict[str, Any]: ...

    @abstractmethod
    async def get_spot_price(self, gpu_type: GPUType, region: str) -> float | None: ...

    @abstractmethod
    async def health_check(self) -> ProviderHealth: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def supports_dedicated_hardware(self) -> bool: ...

    @property
    @abstractmethod
    def compliance_certifications(self) -> list[str]: ...


class RunPodProvider(ProviderInterface):
    """Current production provider. RunPod A40 fleet."""

    def __init__(self) -> None:
        self._api_key = os.environ.get("RUNPOD_API_KEY", "")
        self._api_url = "https://api.runpod.io/graphql"

    @property
    def name(self) -> str:
        return "runpod"

    @property
    def supports_dedicated_hardware(self) -> bool:
        return True

    @property
    def compliance_certifications(self) -> list[str]:
        return ["SOC2"]

    async def list_available_nodes(
        self,
        gpu_type: GPUType | None = None,
        region: str | None = None,
        isolation_level: IsolationLevel | None = None,
    ) -> list[GPUNode]:
        return [
            GPUNode(
                node_id="runpod-a40-001",
                provider="runpod",
                gpu_type=GPUType.A40,
                gpu_count=1,
                vram_gb=48,
                vcpus=16,
                ram_gb=64,
                region="us-east-1",
                zone="us-east-1a",
                status=NodeStatus.AVAILABLE,
                isolation_level=IsolationLevel.SHARED,
                hourly_cost_usd=0.79,
                spot_price_usd=0.50,
                provisioned_at=None,
                last_heartbeat=datetime.now(UTC).isoformat(),
                tenant_id=None,
                compliance_certifications=["SOC2"],
                cuda_version="12.4",
                driver_version="550.54.15",
                network_bandwidth_gbps=10.0,
            )
        ]

    async def provision_node(self, request: ProvisionRequest) -> GPUNode:
        return GPUNode(
            node_id=f"runpod-{int(time.time())}",
            provider="runpod",
            gpu_type=request.gpu_type,
            gpu_count=request.gpu_count,
            vram_gb=48,
            vcpus=16,
            ram_gb=64,
            region=request.region,
            zone=request.region + "a",
            status=NodeStatus.PROVISIONING,
            isolation_level=request.isolation_level,
            hourly_cost_usd=0.79 * request.gpu_count,
            spot_price_usd=None,
            provisioned_at=datetime.now(UTC).isoformat(),
            last_heartbeat=None,
            tenant_id=request.tenant_id,
            compliance_certifications=self.compliance_certifications,
        )

    async def terminate_node(self, node_id: str) -> bool:
        return True

    async def get_node_telemetry(self, node_id: str) -> dict[str, Any]:
        return {
            "node_id": node_id,
            "gpu_utilization": 0.0,
            "gpu_memory_used_gb": 0.0,
            "gpu_temp_c": 45.0,
            "cpu_utilization": 0.0,
            "ram_used_gb": 8.0,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def get_spot_price(self, gpu_type: GPUType, region: str) -> float | None:
        prices = {GPUType.A40: 0.50, GPUType.A100_80GB: 1.20}
        return prices.get(gpu_type)

    async def health_check(self) -> ProviderHealth:
        start = time.time()
        try:
            latency = (time.time() - start) * 1000
            return ProviderHealth(
                provider="runpod",
                healthy=True,
                latency_ms=latency,
                available_nodes=10,
                spot_price_usd=0.50,
                last_checked=datetime.now(UTC).isoformat(),
            )
        except Exception as e:
            return ProviderHealth(
                provider="runpod",
                healthy=False,
                latency_ms=9999,
                available_nodes=0,
                spot_price_usd=None,
                last_checked=datetime.now(UTC).isoformat(),
                error=str(e),
            )


class CoreWeaveProvider(ProviderInterface):
    """CoreWeave — NVIDIA-backed cloud, H100 NVL clusters."""

    def __init__(self) -> None:
        self._api_key = os.environ.get("COREWEAVE_API_KEY", "")
        self._kubeconfig = os.environ.get("COREWEAVE_KUBECONFIG_PATH", "")

    @property
    def name(self) -> str:
        return "coreweave"

    @property
    def supports_dedicated_hardware(self) -> bool:
        return True

    @property
    def compliance_certifications(self) -> list[str]:
        return ["SOC2", "ISO27001", "HIPAA"]

    async def list_available_nodes(
        self,
        gpu_type: GPUType | None = None,
        region: str | None = None,
        isolation_level: IsolationLevel | None = None,
    ) -> list[GPUNode]:
        return [
            GPUNode(
                node_id="cw-h100-001",
                provider="coreweave",
                gpu_type=GPUType.H100_80GB,
                gpu_count=8,
                vram_gb=640,
                vcpus=96,
                ram_gb=384,
                region="us-east-1",
                zone="us-east-1-lga1-1",
                status=NodeStatus.AVAILABLE,
                isolation_level=IsolationLevel.DEDICATED,
                hourly_cost_usd=32.00,
                spot_price_usd=None,
                provisioned_at=None,
                last_heartbeat=None,
                tenant_id=None,
                compliance_certifications=self.compliance_certifications,
                cuda_version="12.3",
                driver_version="545.23.08",
                network_bandwidth_gbps=3200.0,
            )
        ]

    async def provision_node(self, request: ProvisionRequest) -> GPUNode:
        return GPUNode(
            node_id=f"cw-{int(time.time())}",
            provider="coreweave",
            gpu_type=request.gpu_type,
            gpu_count=request.gpu_count,
            vram_gb=80 * request.gpu_count,
            vcpus=96,
            ram_gb=384,
            region=request.region,
            zone=request.region + "-lga1-1",
            status=NodeStatus.PROVISIONING,
            isolation_level=request.isolation_level,
            hourly_cost_usd=4.00 * request.gpu_count,
            spot_price_usd=None,
            provisioned_at=datetime.now(UTC).isoformat(),
            last_heartbeat=None,
            tenant_id=request.tenant_id,
            compliance_certifications=self.compliance_certifications,
        )

    async def terminate_node(self, node_id: str) -> bool:
        return True

    async def get_node_telemetry(self, node_id: str) -> dict[str, Any]:
        return {
            "node_id": node_id,
            "gpu_utilization": 0.0,
            "gpu_memory_used_gb": 0.0,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def get_spot_price(self, gpu_type: GPUType, region: str) -> float | None:
        return None

    async def health_check(self) -> ProviderHealth:
        return ProviderHealth(
            provider="coreweave",
            healthy=bool(self._api_key),
            latency_ms=25.0,
            available_nodes=100,
            spot_price_usd=None,
            last_checked=datetime.now(UTC).isoformat(),
        )


class HardwareProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, ProviderInterface] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(RunPodProvider())
        self.register(CoreWeaveProvider())

    def register(self, provider: ProviderInterface) -> None:
        self._providers[provider.name] = provider

    def get(self, name: str) -> ProviderInterface | None:
        return self._providers.get(name)

    def all(self) -> list[ProviderInterface]:
        return list(self._providers.values())

    async def health_check_all(self) -> dict[str, ProviderHealth]:
        results = await asyncio.gather(
            *[p.health_check() for p in self._providers.values()],
            return_exceptions=True,
        )
        out: dict[str, ProviderHealth] = {}
        for provider, result in zip(self._providers.values(), results, strict=True):
            if isinstance(result, Exception):
                out[provider.name] = ProviderHealth(
                    provider=provider.name,
                    healthy=False,
                    latency_ms=9999,
                    available_nodes=0,
                    spot_price_usd=None,
                    last_checked=datetime.now(UTC).isoformat(),
                    error=str(result),
                )
            else:
                out[provider.name] = result
        return out


_registry: HardwareProviderRegistry | None = None


def get_provider_registry() -> HardwareProviderRegistry:
    global _registry
    if _registry is None:
        _registry = HardwareProviderRegistry()
    return _registry
