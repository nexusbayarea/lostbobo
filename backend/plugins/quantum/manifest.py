from backend.core.sdk.plugin_manifest import (
    IsolationTier,
)
from backend.core.sdk.plugin_manifest import (
    PluginManifest,
)
from backend.core.sdk.plugin_manifest import (
    PluginPermission,
)

manifest = PluginManifest(
    name="quantum",
    version="1.0.0",
    capabilities=[
        "quantum.simulate",
    ],
    dag_nodes=[],
    permissions=[
        PluginPermission.GPU_ALLOCATE,
    ],
    isolation=IsolationTier.KATA,
)
