"""Provenance Graph — scientific audit trail for every Hypothesis."""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from typing import Any

from backend.app.core.supabase import get_supabase_client

log = logging.getLogger(__name__)


@dataclass
class ProvenanceNode:
    node_id: str
    node_type: str
    data: dict[str, Any]
    parent_ids: list[str]
    timestamp: float

    def __post_init__(self):
        if self.parent_ids is None:
            self.parent_ids = []
        if self.timestamp is None:
            self.timestamp = time.time()


class ProvenanceGraph:
    """Supabase-backed provenance for full reproducibility and audit."""

    async def add_node(self, node: ProvenanceNode) -> str:
        sb = get_supabase_client()
        if not sb:
            log.warning("Supabase not available — provenance skipped")
            return node.node_id

        payload = {
            "node_type": node.node_type,
            "data": node.data,
            "parent_ids": node.parent_ids,
            "timestamp": node.timestamp,
        }
        node_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]

        try:
            sb.table("provenance_nodes").insert(
                {
                    "node_id": node.node_id,
                    "node_hash": node_hash,
                    "node_type": node.node_type,
                    "data": node.data,
                    "parent_ids": node.parent_ids,
                    "created_at": "now()",
                }
            ).execute()
            log.info("Provenance node recorded: %s (%s)", node.node_id, node.node_type)
        except Exception as e:
            log.error("Failed to record provenance: %s", e)

        return node.node_id
