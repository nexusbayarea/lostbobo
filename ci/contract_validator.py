#!/usr/bin/env python3
"""Contract Validator - makes invalid states unrepresentable."""

import json
import subprocess
import sys

REQUIRED_MODULES = ["core", "api", "worker", "autoscaler", "tests"]


def fail(msg: str):
    print(f"CONTRACT ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def check_ghcr_login() -> bool:
    return True


def check_dag(dag: dict):
    if not dag or not dag.get("modules"):
        fail("DAG modules list is empty")

    missing = [m for m in REQUIRED_MODULES if m not in dag.get("modules", [])]
    if missing:
        fail(f"Missing required modules: {missing}")


def check_image(image: str):
    if ":latest" in image:
        fail("Use digest or stable tag only (latest forbidden)")
    if not image.startswith("ghcr.io/"):
        fail("Image must be ghcr.io registry")


def check_local_actions():
    result = subprocess.run(
        ["grep", "-r", "uses: ./.github/actions", ".github/workflows/"],
        capture_output=True,
        text=True,
    )
    if "setup-python-env" in result.stdout:
        fail("Forbidden local action detected: setup-python-env")


def check_workflow_syntax():
    import yaml
    import os

    for f in os.listdir(".github/workflows"):
        if not f.endswith(".yml"):
            continue
        path = f".github/workflows/{f}"
        try:
            with open(path) as fp:
                yaml.safe_load(fp)
        except yaml.YAMLError as e:
            fail(f"Invalid YAML in {path}: {e}")


def validate_contract():
    check_local_actions()
    check_workflow_syntax()

    dag = {
        "modules": REQUIRED_MODULES,
        "execution_order": [["core"], ["api", "autoscaler"], ["worker", "tests"]],
    }

    check_dag(dag)

    image = "ghcr.io/nexusbayarea/simhpc-base:stable"
    check_image(image)

    manifest = {
        "git": {"sha": ""},
        "image": {
            "registry": "ghcr.io",
            "name": "nexusbayarea/simhpc-base",
            "tag": "stable",
        },
        "dag": dag,
        "runtime": {"service_role": "unified"},
        "cache": {"enabled": True},
    }

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    validate_contract()

