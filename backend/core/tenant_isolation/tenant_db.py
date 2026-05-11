from backend.app.core.supabase import get_supabase_client
from backend.core.tenant_isolation.tenant import get_tenant_from_context


class TenantScopedClient:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self._raw = get_supabase_client()

    def table(self, name: str):
        q = self._raw.table(name)
        if name in {"plugin_registry", "plugin_permissions"}:  # global tables
            return q
        return q.eq("tenant_id", self.tenant_id)


def get_tenant_db():
    tenant_id = get_tenant_from_context()
    return TenantScopedClient(tenant_id)
