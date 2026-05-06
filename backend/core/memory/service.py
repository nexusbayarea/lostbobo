"""Memory Service — persistent decision-outcome ledger."""

from __future__ import annotations

import logging
from typing import Any

from backend.app.core.supabase import get_supabase_client
from backend.core.memory.schema import MemoryRecord
from backend.core.redis.beam_streamer import BeamStreamer

log = logging.getLogger(__name__)


class MemoryService:
    def __init__(self):
        self.streamer = BeamStreamer()

    async def record(self, record: MemoryRecord) -> MemoryRecord:
        """Store decision / observation / outcome."""
        sb = get_supabase_client()
        if not sb:
            log.warning("Supabase unavailable — memory record skipped")
            return record

        await (
            sb.table("memory_records")
            .insert(
                {
                    "id": record.id,
                    "type": record.type,
                    "timestamp": record.timestamp.isoformat(),
                    "context": record.context,
                    "content": record.content,
                    "outcome": record.outcome,
                    "links": record.links,
                    "tenant_id": record.tenant_id,
                }
            )
            .execute()
        )

        await self.streamer._publish_event(
            f"memory_{record.id}",
            {
                "event": "memory_recorded",
                "type": record.type,
                "timestamp": record.timestamp.isoformat(),
                "confidence": record.content.get("confidence"),
            },
        )

        log.info("Memory recorded: %s (%s)", record.id, record.type)
        return record

    async def query(self, filter: dict[str, Any], limit: int = 50) -> list[MemoryRecord]:
        """Structured query over memory ledger."""
        sb = get_supabase_client()
        if not sb:
            return []

        query = sb.table("memory_records").select("*")

        if "domain" in filter:
            query = query.eq("context->>domain", filter["domain"])
        if "type" in filter:
            query = query.eq("type", filter["type"])
        if "error_threshold" in filter:
            query = query.gt("outcome->>error", filter["error_threshold"])

        resp = await query.order("timestamp", desc=True).limit(limit).execute()
        return [MemoryRecord(**r) for r in resp.data]

    async def reconcile(self, memory_id: str, observed_outcome: dict[str, Any]) -> MemoryRecord | None:
        """Close the loop: attach real outcome and compute error."""
        sb = get_supabase_client()
        if not sb:
            return None

        resp = await sb.table("memory_records").select("*").eq("id", memory_id).execute()
        if not resp.data:
            return None

        record = MemoryRecord(**resp.data[0])
        record.outcome["observed"] = observed_outcome
        record.outcome["error"] = abs(observed_outcome.get("value", 0) - record.outcome.get("expected", 0))

        await (
            sb.table("memory_records")
            .update(
                {
                    "outcome": record.outcome,
                }
            )
            .eq("id", memory_id)
            .execute()
        )

        log.info("Memory reconciled: %s (error: %.3f)", memory_id, record.outcome["error"])
        return record
