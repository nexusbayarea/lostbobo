from __future__ import annotations

import importlib
import pkgutil

from backend.core.sdk.base_plugin import BasePlugin


class PluginLoader:
    def __init__(
        self,
        kernel,
        plugin_package: str = "backend.plugins",
    ) -> None:
        self.kernel = kernel
        self.plugin_package = plugin_package

    async def load_plugins(self) -> None:
        package = importlib.import_module(self.plugin_package)

        for _, module_name, _ in pkgutil.iter_modules(package.__path__):
            plugin_module = importlib.import_module(f"{self.plugin_package}.{module_name}.plugin")

            plugin_cls = plugin_module.Plugin

            plugin: BasePlugin = plugin_cls()

            await plugin.register(self.kernel)

            self.kernel.logger.info(
                "Loaded plugin: %s",
                plugin.manifest.name,
            )
