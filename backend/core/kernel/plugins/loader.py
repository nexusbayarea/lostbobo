"""Plugin Auto-Registration System."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from backend.core.kernel.plugins.gamma_module import GammaModule

if TYPE_CHECKING:
    from backend.core.kernel.world_brain import WorldBrain

log = logging.getLogger(__name__)


class PluginLoader:
    def __init__(self, world_brain: WorldBrain):
        self.world_brain = world_brain
        self.modules: dict[str, GammaModule] = {}

    def discover_and_register(self):
        """Auto-discover Gamma modules in plugins/gamma/"""
        try:
            import inspect

            from backend.core.kernel.plugins import gamma

            for _name, obj in inspect.getmembers(gamma):
                if inspect.isclass(obj) and issubclass(obj, GammaModule) and obj != GammaModule:
                    instance = obj()
                    self.modules[instance.name] = instance
                    log.info("Gamma Module loaded: %s", instance.name)
        except Exception as e:
            log.warning("Failed to load gamma modules: %s", e)
