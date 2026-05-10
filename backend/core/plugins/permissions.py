from .capabilities import Capability
from .manifests import PluginManifest


class PermissionManager:
    def validate(self, manifest: PluginManifest, capability: Capability) -> bool:
        if capability.value not in manifest.permissions:
            raise PermissionError(f"Plugin '{manifest.name}' lacks required capability: {capability.value}")
        return True
