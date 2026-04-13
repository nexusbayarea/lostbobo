#!/usr/bin/env python3
"""
Deterministic Change Detection Script.

Outputs changed modules as comma-separated list for CI skip logic.
If detection fails, outputs ALL modules to ensure full graph runs.
"""

import subprocess
import sys

ALL_MODULES = "app,worker,api,autoscaler,tests,scripts,frontend,docker,ci,dependency"


def get_changed_files(base_sha: str = "HEAD~1", head: str = "HEAD") -> list[str]:
    """Get list of changed files between commits."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base_sha, head],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return []
        return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except Exception:
        return []


def map_files_to_modules(files: list[str]) -> list[str]:
    """Map changed files to their containing modules."""
    modules = set()
    for f in files:
        if f.startswith("app/"):
            modules.add("app")
        elif f.startswith("worker/"):
            modules.add("worker")
        elif f.startswith("app/api/"):
            modules.add("api")
        elif f.startswith("autoscaler/"):
            modules.add("autoscaler")
        elif f.startswith("tests/"):
            modules.add("tests")
        elif f.startswith("scripts/"):
            modules.add("scripts")
        elif f.startswith("frontend/"):
            modules.add("frontend")
        elif f.startswith("docker/"):
            modules.add("docker")
        elif f in ["pyproject.toml", "uv.lock", "requirements.lock"]:
            modules.add("dependency")
        elif (f.endswith(".yml") or f.endswith(".yaml")) and ".github/" in f:
            modules.add("ci")

    return list(modules)


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "HEAD~1"
    head = sys.argv[2] if len(sys.argv) > 2 else "HEAD"

    files = get_changed_files(base, head)

    if not files:
        print(ALL_MODULES)
        sys.exit(0)

    modules = map_files_to_modules(files)

    if not modules:
        print(ALL_MODULES)
        sys.exit(0)

    print(",".join(sorted(modules)))


if __name__ == "__main__":
    main()
