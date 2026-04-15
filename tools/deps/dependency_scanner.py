#!/usr/bin/env python3
"""
Dependency Graph Scanner - extracts imports from DAG nodes
"""

import ast
from pathlib import Path
from typing import Set


def extract_imports(file_path: Path) -> Set[str]:
    if not file_path.exists():
        return set()

    with open(file_path, "r") as f:
        try:
            tree = ast.parse(f.read(), filename=str(file_path))
        except SyntaxError:
            return set()

    imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name.split(".")[0])

        if isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])

    return imports


def scan_project(paths: list) -> Set[str]:
    all_imports = set()

    for p in paths:
        all_imports |= extract_imports(Path(p))

    return all_imports


if __name__ == "__main__":
    files = [
        "tools/bootstrap.py",
        "tools/runtime/dag_executor.py",
        "tools/ci_gates/system_contract.py",
    ]

    imports = scan_project(files)
    print(f"Found imports: {sorted(imports)}")
