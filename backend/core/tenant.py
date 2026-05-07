def tenant_key(base: str, tenant_id: str) -> str:
    """All Redis keys must be tenant-scoped"""
    return f"tenant:{tenant_id}:{base}"
