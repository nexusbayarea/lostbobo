from __future__ import annotations

from typing import Any

from backend.core.sdk.abi.plugin_manifest import SecretScope


class SecretResolver:
    def __init__(self, infisical_client: Any | None = None):
        self._client = infisical_client

    async def resolve(self, scopes: list[SecretScope], plugin_name: str) -> dict[str, str]:
        if not scopes:
            return {}
        if self._client is None:
            return self._resolve_local(scopes, plugin_name)
        return await self._resolve_infisical(scopes)

    def _resolve_local(self, scopes: list[SecretScope], plugin_name: str) -> dict[str, str]:
        import os

        secrets: dict[str, str] = {}
        for scope in scopes:
            env_key = scope.secret_path.replace("/", "_").replace("-", "_").upper()
            value = os.environ.get(env_key)
            if value:
                secrets[scope.secret_path] = value
            else:
                env_key_plugin = f"PLUGIN_{plugin_name.upper()}_SECRET"
                value = os.environ.get(env_key_plugin)
                if value:
                    secrets[scope.secret_path] = value
        return secrets

    async def _resolve_infisical(self, scopes: list[SecretScope]) -> dict[str, str]:
        secrets: dict[str, str] = {}
        for scope in scopes:
            secrets[scope.secret_path] = ""
        return secrets


class SecretResolverError(Exception):
    pass
