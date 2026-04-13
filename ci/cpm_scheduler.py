#!/usr/bin/env python3
"""Critical Path Method scheduler with priority queue."""

import json
import heapq


def compute_critical_path(dag):
    """Compute criticality score for each node using reverse DFS."""
    graph = {n["name"]: n for n in dag}
    memo = {}

    def dfs(node_name):
        if node_name in memo:
            return memo[node_name]

        node = graph[node_name]
        children = [
            child["name"] for child in dag if node_name in child.get("deps", [])
        ]

        if not children:
            runtime = node.get("estimated_runtime", 1)
            memo[node_name] = runtime
            return runtime

        runtime = node.get("estimated_runtime", 1)
        max_child = max(dfs(c) for c in children) if children else 0
        score = runtime + max_child

        memo[node_name] = score
        return score

    for node in dag:
        dfs(node["name"])

    return memo


def build_priority_queue(nodes, criticality):
    """Max-heap ordered by criticality (highest first)."""
    heap = []
    for node in nodes:
        score = criticality.get(node["name"], 1)
        heapq.heappush(heap, (-score, node))
    return heap


def get_ready_nodes(dag, completed, skipped):
    """Nodes with all deps completed and not cached."""
    done = completed.union(skipped)
    ready = []

    for node in dag:
        if node["name"] in done:
            continue

        deps = node.get("deps", [])
        if all(dep in done for dep in deps):
            ready.append(node)

    return ready


def schedule(dag, cache):
    """Full priority-scheduled execution order."""
    criticality = compute_critical_path(dag)

    skipped = set()
    for node in dag:
        if node["name"] in cache:
            skipped.add(node["name"])

    ready = get_ready_nodes(dag, set(), skipped)
    heap = build_priority_queue(ready, criticality)

    ordered = []
    while heap:
        _, node = heapq.heappop(heap)
        ordered.append(node)

        done = set(k for k in cache.keys())
        done.update(n["name"] for n in ordered)
        done.update(skipped)

        new_ready = get_ready_nodes(dag, done, skipped)
        for nr in new_ready:
            if nr not in [n["name"] for n in ordered]:
                score = criticality.get(nr["name"], 1)
                heapq.heappush(heap, (-score, nr))

    return ordered


def main():
    import sys

    manifest = sys.argv[1] if len(sys.argv) > 1 else "build-manifest.json"

    with open(manifest) as f:
        data = json.load(f)

    dag = data.get("dag", {}).get("jobs", [])

    cached = {}
    if ".cache/dag_cache.json":
        try:
            with open(".cache/dag_cache.json") as cf:
                cached = json.load(cf)
        except:
            pass

    ordered = schedule(dag, cached)

    result = {
        "schedule": [n["name"] for n in ordered],
        "criticality": compute_critical_path(dag),
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
