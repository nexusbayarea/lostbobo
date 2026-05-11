"""
backend/core/middleware/llm_cost_gate.py
LLM Cost Gate — Hard budget enforcement (Supabase-backed)
"""

from dataclasses import dataclass
from datetime import datetime

from backend.app.core.supabase import get_supabase_client

MODEL_PRICING = {
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5": {"input": 0.25, "output": 1.25},
}

TIER_MONTHLY_BUDGETS = {
    "free": 5.0,
    "professional": 50.0,
    "enterprise": 500.0,
    "defense": 2000.0,
}


@dataclass
class CostCheckResult:
    allowed: bool
    reason: str = ""


class LLMCostGate:
    def __init__(self):
        self._db = get_supabase_client()

    async def guarded_llm_call(
        self,
        tenant_id: str,
        plugin_name: str,
        model: str,
        messages: list,
        max_tokens: int,
        sla_tier: str = "free",
        **kwargs,
    ):
        # 1. Budget check
        check = await self._pre_call_check(tenant_id, sla_tier)
        if not check.allowed:
            raise RuntimeError(f"LLM call blocked: {check.reason}")

        # 2. Make the call (placeholder)
        import anthropic

        client = anthropic.Anthropic()
        response = client.messages.create(model=model, max_tokens=max_tokens, messages=messages, **kwargs)

        # 3. Record usage
        await self._record_usage(tenant_id, plugin_name, model, response)

        return response

    async def _pre_call_check(self, tenant_id: str, sla_tier: str):
        # Check utilization via view
        response = (
            self._db.table("budget_utilization")
            .select("budget_exhausted, utilization_pct")
            .eq("tenant_id", tenant_id)
            .single()
            .execute()
        )

        data = response.data
        if data and data.get("budget_exhausted"):
            return CostCheckResult(allowed=False, reason="Monthly budget exhausted")

        return CostCheckResult(allowed=True)

    async def _record_usage(self, tenant_id: str, plugin_name: str, model: str, response):
        pricing = MODEL_PRICING.get(model, {"input": 0, "output": 0})
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = input_tokens * pricing["input"] / 1_000_000 + output_tokens * pricing["output"] / 1_000_000

        self._db.table("llm_usage").insert(
            {
                "tenant_id": tenant_id,
                "plugin_name": plugin_name,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost,
                "month_key": datetime.now().strftime("%Y-%m"),
            }
        ).execute()

    async def get_spend_report(self, tenant_id: str):
        response = self._db.table("llm_spend_current_month").select("*").eq("tenant_id", tenant_id).single().execute()
        return response.data


_gate = None


def get_llm_cost_gate() -> LLMCostGate:
    global _gate
    if _gate is None:
        _gate = LLMCostGate()
    return _gate
