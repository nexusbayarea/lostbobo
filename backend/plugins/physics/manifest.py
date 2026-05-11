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
    name="physics",
    version="1.0.0",
    capabilities=[
        "physics.solve",
        "physics.simulate",
    ],
    dag_nodes=[
        "beam.solve",
    ],
    permissions=[
        PluginPermission.GPU_ALLOCATE,
        PluginPermission.DAG_EXECUTE,
    ],
    isolation=IsolationTier.KATA,
)
