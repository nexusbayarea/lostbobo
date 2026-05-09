import hashlib
import json
from datetime import datetime

from backend.app.core.supabase import get_supabase_client
from backend.core.services.observability_service import observability
from backend.services.compliance.models import AuditEventType, AuditOutcome


class AuditLog:
    def __init__(self):
        self.supabase = get_supabase_client()

    async def log(self, event_type: AuditEventType, outcome: AuditOutcome, **kwargs):
        data = {**kwargs, "timestamp": datetime.utcnow().isoformat()}
        entry_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

        entry = {
            "event_type": event_type.value,
            "outcome": outcome.value,
            **kwargs,
            "entry_hash": entry_hash,
            "hash_chain": f"chain_{hashlib.sha256((str(datetime.utcnow()) + entry_hash).encode()).hexdigest()}",
            "previous_entry_hash": "genesis",
        }

        await self.supabase.table("audit_log").insert(entry).execute()
        observability().increment("audit_log_entries_total", {"event_type": event_type.value})


def get_audit_log():
    return AuditLog()
