from __future__ import annotations

from backend.core.sdk.runtime.plugin_context import PluginContext


class PluginRuntime:
    def __init__(self, kernel):
        self.kernel = kernel

    async def boot_plugin(self, plugin):
        context = PluginContext(
            tenant_id="__system__",
            plugin_name=plugin.manifest.name,
            run_id="boot",
            kernel=self.kernel,
        )

        # deterministic lifecycle order
        await plugin.pre_boot(context)
        await plugin.register(context)
        await plugin.post_boot(context)

        self.kernel.logger.info("Plugin booted: %s", plugin.manifest.name)
