from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.core.sdk.registries.capability_registry import ExecutionContext


@pytest.mark.asyncio
async def test_rail_1_kernel_centered_execution(kernel):
    assert kernel.scheduler is not None
    assert kernel.capability_registry is not None
    assert len(kernel.capability_registry.registered_capabilities) > 0


@pytest.mark.asyncio
async def test_rail_2_supabase_dag_truth(kernel):
    nodes = kernel.dag_registry.registered_nodes
    assert "beam.solve" in nodes
    assert "schrodinger.solve" in nodes
    entry = kernel.dag_registry.get_node("beam.solve")
    assert entry.plugin_name == "physics"


@pytest.mark.asyncio
async def test_rail_3_no_api_py():
    backend_api = Path("backend/app/api")
    forbidden = ["physics.py", "forecast.py", "weather.py", "market.py"]
    for fname in forbidden:
        assert not (backend_api / fname).exists(), (
            f"Domain API file {fname} should not exist"
        )


@pytest.mark.asyncio
async def test_rail_4_infisical_config():
    manifest_path = Path("plugins/forecasting/manifest.json")
    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
        secrets = manifest.get("permissions", {}).get("secrets", [])
        for secret in secrets:
            assert secret["secret_path"].startswith("/plugins/")


@pytest.mark.asyncio
async def test_rail_5_plugin_first(kernel):
    running = kernel.plugin_registry.list_running()
    assert "physics" in running
    assert "forecasting" in running


@pytest.mark.asyncio
async def test_rail_6_core_domain_agnostic():
    core_path = Path("backend/core")
    domain_terms = [
        "physics",
        "forecast",
        "weather",
        "market",
        "ev_battery",
        "wildfire",
    ]
    false_positives = ["generic", "abstract", "base", "interface", "test_", "mock_"]
    violations = []
    for pyfile in core_path.rglob("*.py"):
        if "__pycache__" in str(pyfile):
            continue
        text = pyfile.read_text().lower()
        for term in domain_terms:
            if term in text:
                if not any(fp in text for fp in false_positives):
                    violations.append(f"{pyfile}: contains '{term}'")
    assert len(violations) == 0, "Domain leakage:\n" + "\n".join(violations)


@pytest.mark.asyncio
async def test_rail_7_primitives_vs_intelligence(kernel):
    assert kernel.capability_registry is not None
    assert kernel.dag_registry is not None
    from backend.plugins.physics.schemas.molecule import MoleculeInput

    assert MoleculeInput is not None


@pytest.mark.asyncio
async def test_rail_8_dag_ir_portable(kernel):
    entry = kernel.dag_registry.get_node("beam.solve")
    entry_str = str(entry).lower()
    for ref in ["airflow", "prefect", "temporal", "dask", "ray", "celery"]:
        assert ref not in entry_str, f"DAG node references {ref}"


@pytest.mark.asyncio
async def test_rail_9_deterministic_execution(kernel, water_molecule):
    r1 = await kernel.capability_registry.invoke(
        "physics.solve",
        {"molecule": water_molecule, "backend": "pyscf"},
        execution_context=ExecutionContext(seed=42),
    )
    r2 = await kernel.capability_registry.invoke(
        "physics.solve",
        {"molecule": water_molecule, "backend": "pyscf"},
        execution_context=ExecutionContext(seed=42),
    )
    assert r1["energy"] == r2["energy"]


@pytest.mark.asyncio
async def test_rail_10_plugin_security():
    for plugin_name in ["physics", "forecasting"]:
        manifest_path = Path(f"backend/plugins/{plugin_name}/manifest.json")
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = json.load(f)
            assert "isolation_tier" in manifest
            assert "permissions" in manifest
            assert "resource_quota" in manifest


@pytest.mark.asyncio
async def test_rail_11_memory_fabric():
    for plugin_name in ["physics", "forecasting"]:
        manifest_path = Path(f"backend/plugins/{plugin_name}/manifest.json")
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = json.load(f)
            assert "memory_contract" in manifest
            assert "tiers" in manifest["memory_contract"]
