"""
Dependency Scanner — Detects missing runtime dependencies before execution

Run as first bootstrap stage to fail fast on missing deps instead of at runtime.
"""

import ast
import sys
from pathlib import Path

ROOT = Path(".")

STDLIB = {
    "os",
    "sys",
    "math",
    "json",
    "time",
    "datetime",
    "pathlib",
    "typing",
    "collections",
    "itertools",
    "asyncio",
    "re",
    "subprocess",
    "contextlib",
    "enum",
    "uuid",
    "hashlib",
    "secrets",
    "random",
    "base64",
    "functools",
    "operator",
    "copy",
    "io",
    "abc",
}


def extract_imports() -> set:
    deps = set()

    for file in ROOT.rglob("*.py"):
        path = str(file)
        if "venv" in path or ".git" in path or ".venv" in path or "__pycache__" in path:
            continue

        try:
            tree = ast.parse(file.read_text())
        except Exception:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    deps.add(n.name.split(".")[0])

            if isinstance(node, ast.ImportFrom) and node.module:
                deps.add(node.module.split(".")[0])

    return deps


def check_requirements() -> None:
    reqs_path = Path("requirements.txt")
    if not reqs_path.exists():
        print("ERROR: requirements.txt not found")
        sys.exit(1)

    reqs = reqs_path.read_text().lower()

    detected = extract_imports()
    filtered = sorted([d for d in detected if d not in STDLIB])

    missing = []
    for dep in filtered:
        if dep not in reqs and dep.replace("_", "-") not in reqs:
            missing.append(dep)

    if missing:
        print("\nMISSING DEPENDENCIES DETECTED:")
        for m in missing:
            print(f" - {m}")
        print("\nAdd these to requirements.txt before running CI")
        sys.exit(1)

    print(f"Dependency scan OK: {len(filtered)} packages verified")


if __name__ == "__main__":
    check_requirements()
