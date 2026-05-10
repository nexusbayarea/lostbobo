# backend/core/kernel/kernel.py
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from backend.core.kernel.command_bus import CommandBus
from backend.core.kernel.lineage.collector import LineageCollector
from backend.core.services.observability_service import observability
from backend.core.tracing import trace_context


class SimHPCKernel:
    """Main SimHPC Kernel with unified lineage tracking."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.command_bus = CommandBus()
            cls._instance.lineage = LineageCollector.collector()
        return cls._instance

    @classmethod
    def kernel(cls) -> SimHPCKernel:
        return cls()

    async def execute(self, command: dict[str, Any]) -> dict[str, Any]:
        """Execute any command with full lineage tracking."""
        execution_id = command.get("execution_id") or str(uuid.uuid4())

        with trace_context("kernel.execute", {"execution_id": execution_id}) as span:
            try:
                # 1. Record execution start
                await self.lineage.emit(
                    execution_id=execution_id,
                    event_type="execution_started",
                    source_type="kernel",
                    source_id="simhpc_kernel",
                    payload={
                        "command_type": command.get("type"),
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

                # 2. Execute command through bus
                result = await self.command_bus.execute(command)

                # 3. Record successful completion
                await self.lineage.emit(
                    execution_id=execution_id,
                    event_type="execution_completed",
                    source_type="kernel",
                    source_id="simhpc_kernel",
                    payload={
                        "success": True,
                        "duration_ms": span.get_duration_ms(),
                        "result_summary": str(result)[:500],
                    },
                )

                observability().increment("kernel_executions_success")
                return {"execution_id": execution_id, "result": result}

            except Exception as e:
                # 4. Record failure
                await self.lineage.emit(
                    execution_id=execution_id,
                    event_type="execution_failed",
                    source_type="kernel",
                    source_id="simhpc_kernel",
                    payload={
                        "error": str(e),
                        "error_type": type(e).__name__,
                    },
                )
                observability().increment("kernel_executions_failed")
                raise
