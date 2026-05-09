from __future__ import annotations

from pydantic import BaseModel

from backend.app.core.supabase import get_supabase_client
from backend.core.kernel.command_bus import command_bus
from backend.core.services.observability_service import observability
from backend.core.tracing import trace_context


class ResourceQuota(BaseModel):
    cpu_cores: float = 8.0
    memory_mb: int = 8192
    gpu_hours: float = 4.0
    inference_tokens_per_min: int = 100_000
    max_graph_nodes: int = 5000
    max_graph_edges: int = 20_000


class ResourceGovernor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._supabase = get_supabase_client()
            cls._instance._quotas: dict[str, ResourceQuota] = {}
        return cls._instance

    @classmethod
    def governor(cls) -> ResourceGovernor:
        return cls()

    async def check(self, tenant_id: str = "default", command: str = "") -> bool:
        """Enforce hard/soft limits before any command execution."""
        with trace_context("resource.check", {"tenant": tenant_id, "command": command}):
            obs = observability()

            quota = await self._get_quota(tenant_id)
            usage = self._get_current_usage(tenant_id)

            # Hard limits (immediate rejection)
            if usage.get("cpu_cores", 0) >= quota.cpu_cores * 1.1 or usage.get("memory_mb", 0) >= quota.memory_mb * 1.1:
                obs.increment("resource_hard_limit_exceeded", tags={"tenant": tenant_id})
                await command_bus.execute("RESOURCE_REJECT", reason="hard_limit")
                return False

            # Soft limits (warning + backpressure)
            if usage.get("inference_tokens_per_min", 0) > quota.inference_tokens_per_min * 0.8:
                obs.increment("resource_soft_limit_warning")
                # Apply backpressure
                await command_bus.execute("BACKPRESSURE_APPLY", level="soft")

            obs.gauge("resource_utilization", usage)
            return True

    async def _get_quota(self, tenant_id: str) -> ResourceQuota:
        if tenant_id in self._quotas:
            return self._quotas[tenant_id]

        # Supabase override
        row = (
            await self._supabase.table("resource_allocations").select("*").eq("tenant_id", tenant_id).limit(1).execute()
        )
        data = row.data[0] if row.data else {}

        quota = ResourceQuota(**data)
        self._quotas[tenant_id] = quota
        return quota

    def _get_current_usage(self, tenant_id: str) -> dict:
        # Real-time usage from observability
        return observability().get_resource_usage(tenant_id)
