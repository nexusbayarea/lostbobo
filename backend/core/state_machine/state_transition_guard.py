from __future__ import annotations

from backend.core.state_machine.kernel_state import KernelState


class StateTransitionGuard:
    VALID_TRANSITIONS = {
        KernelState.PENDING: [KernelState.QUEUED, KernelState.CANCELLED],
        KernelState.QUEUED: [KernelState.SCHEDULED, KernelState.CANCELLED],
        KernelState.SCHEDULED: [KernelState.RUNNING, KernelState.FAILED],
        KernelState.RUNNING: [
            KernelState.COMPLETED,
            KernelState.FAILED,
            KernelState.PAUSED,
            KernelState.CHECKPOINTING,
        ],
        KernelState.PAUSED: [KernelState.RUNNING, KernelState.CANCELLED],
        KernelState.CHECKPOINTING: [KernelState.RUNNING, KernelState.FAILED],
        KernelState.REPLAYING: [KernelState.COMPLETED, KernelState.FAILED],
        KernelState.FAILED: [KernelState.PENDING],
    }

    @classmethod
    def validate(cls, current: KernelState, target: KernelState) -> bool:
        allowed = cls.VALID_TRANSITIONS.get(current, [])
        if target not in allowed:
            raise RuntimeError(f"Invalid state transition: {current} -> {target}")
        return True
