from __future__ import annotations


class PluginContext:
    def __init__(
        self,
        tenant_id: str,
        plugin_name: str,
        run_id: str,
        kernel,
    ):
        self.tenant_id = tenant_id
        self.plugin_name = plugin_name
        self.run_id = run_id
        self.kernel = kernel

    @property
    def capabilities(self):
        return self.kernel.capabilities

    @property
    def events(self):
        return self.kernel.events

    @property
    def memory(self):
        return self.kernel.memory

    @property
    def lineage(self):
        return self.kernel.lineage
