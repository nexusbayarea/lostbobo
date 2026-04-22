import ast
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"

VIOLATIONS = []


def is_outside_backend(module: str) -> bool:
    root = module.split(".")[0]
    allowed = {"app", "runtime", "compiler", "services", "worker", "packages", "autoscaler", "skills"}
    return root not in allowed


def scan_file(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(path))
    except Exception as e:
        print(f"Warning: Could not parse {path}: {e}")
        return

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and is_outside_backend(node.module):
                VIOLATIONS.append((str(path), node.module, "ImportFrom"))

        if isinstance(node, ast.Import):
            for n in node.names:
                if is_outside_backend(n.name):
                    VIOLATIONS.append((str(path), n.name, "Import"))


def scan():
    for base, _, files in os.walk(BACKEND):
        for f in files:
            if f.endswith(".py"):
                scan_file(Path(base) / f)


if __name__ == "__main__":
    scan()

    if VIOLATIONS:
        print("\nRUNTIME ISOLATION VIOLATIONS:\n")
        for v in VIOLATIONS:
            print(f" - {v[0]} → {v[1]} ({v[2]})")
        sys.exit(1)

    print("Runtime isolation OK")