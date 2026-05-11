from backend.core.sdk.plugin_manifest import (
    IsolationTier,
    PluginManifest,
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
