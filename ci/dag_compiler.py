#!/usr/bin/env python3
"""DAG Compiler - single source of truth for execution graph."""

import json


def load_module_graph():
    try:
        with open("ci/module_graph.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "core": {"paths": ["app/core"], "deps": []},
            "api": {"paths": ["app/api"], "deps": ["core"]},
            "worker": {"paths": ["worker", "app/services/worker"], "deps": ["core"]},
        }


def get_changed_files(base="origin/main", head="HEAD"):
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base}...{head}"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return []
        return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except Exception:
        return []


def match_modules(files, graph):
    affected = set()
    for f in files:
        for module, data in graph.items():
            for path in data.get("paths", []):
                if f.startswith(path):
                    affected.add(module)
                    break
    return affected


def expand_deps(modules, graph):
    expanded = set(modules)

    def visit(m):
        for dep in graph.get(m, {}).get("deps", []):
            if dep not in expanded:
                expanded.add(dep)
                visit(dep)

    for m in list(modules):
        visit(m)

    return expanded


def topo_sort(graph):
    visited = set()
    order = []

    def visit(node):
        if node in visited:
            return
        visited.add(node)
        for dep in graph.get(node, {}).get("deps", []):
            visit(dep)
        order.append(node)

    for node in graph:
        visit(node)

    return order


def compute_dag(base="origin/main", head="HEAD"):
    graph = load_module_graph()
    files = get_changed_files(base, head)

    if not files:
        modules = set(graph.keys())
    else:
        affected = match_modules(files, graph)
        modules = expand_deps(affected, graph)

    order = topo_sort(graph)

    execution_order = []
    current_stage = []

    for module in order:
        if module not in modules:
            continue

        deps = graph.get(module, {}).get("deps", [])
        has_pending_deps = any(d in current_stage for d in deps)

        if has_pending_deps and current_stage:
            execution_order.append(current_stage)
            current_stage = []

        current_stage.append(module)

    if current_stage:
        execution_order.append(current_stage)

    return {
        "modules": list(modules),
        "execution_order": execution_order,
    }


def main():
    import sys

    base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    head = sys.argv[2] if len(sys.argv) > 2 else "HEAD"

    dag = compute_dag(base, head)
    print(json.dumps(dag))


if __name__ == "__main__":
    main()
