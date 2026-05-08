from typing import Any


class FlywheelHooks:
    """Hooks for integrating flywheel updates into simulation runners."""

    @staticmethod
    async def pre_run_hook(config: dict[str, Any], tenant_id: str) -> dict[str, Any]:
        # Logic to inject priors
        return config

    @staticmethod
    async def post_run_hook(
        run_id: str, tenant_id: str, result: dict[str, Any], config: dict[str, Any]
    ) -> dict[str, Any]:
        # Logic to ingest result into flywheel
        return result
