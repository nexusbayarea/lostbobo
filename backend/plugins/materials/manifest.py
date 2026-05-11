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
    name="materials",
    version="1.0.0",
    capabilities=[
        "materials.predict",
    ],
    dag_nodes=[],
    permissions=[
        PluginPermission.GPU_ALLOCATE,
    ],
    isolation=IsolationTier.KATA,
)
