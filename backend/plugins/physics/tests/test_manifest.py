from __future__ import annotations

import json
from pathlib import Path

from backend.core.sdk.abi.plugin_manifest import PluginManifest


def test_manifest_is_valid():
    manifest_path = Path(__file__).parent.parent / "manifest.json"
    with open(manifest_path) as f:
        data = json.load(f)
    manifest = PluginManifest(**data)
    assert manifest.name == "physics"
    assert manifest.version == "1.0.0"
    assert "physics.solve" in manifest.capabilities
    assert len(manifest.dag_nodes) == 2
    assert manifest.dag_nodes[0].node_type == "beam.solve"
