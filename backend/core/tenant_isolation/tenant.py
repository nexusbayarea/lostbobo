"""
backend/core/tenant_isolation/tenant.py
Tenant context with ContextVar for async propagation.
"""

import contextvars
import logging
from dataclasses import dataclass

log = logging.getLogger(__name__)

SYSTEM_TENANT_ID = "__system__"
UNKNOWN_TENANT = "__unknown__"

_tenant_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("tenant_id", default=UNKNOWN_TENANT)


def get_tenant_from_context() -> str:
    tenant_id = _tenant_ctx.get()
    if tenant_id == UNKNOWN_TENANT:
        raise RuntimeError("No tenant context set. Use TenantMiddleware or set_system_tenant_context().")
    return tenant_id


def set_tenant_context(tenant_id: str) -> contextvars.Token:
    if not tenant_id:
        raise ValueError("tenant_id cannot be empty")
    token = _tenant_ctx.set(tenant_id)
    log.debug("Tenant context set: %s", tenant_id)
    return token


def reset_tenant_context(token: contextvars.Token):
    _tenant_ctx.reset(token)


def set_system_tenant_context() -> contextvars.Token:
    return set_tenant_context(SYSTEM_TENANT_ID)


@dataclass(frozen=True)
class TenantContext:
    tenant_id: str
    user_id: str
    user_role: str
    is_system: bool = False

    @classmethod
    def system(cls):
        return cls(SYSTEM_TENANT_ID, "system", "admin", True)
