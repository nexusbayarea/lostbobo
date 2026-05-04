from typing import Any


def normalize(value: Any) -> Any:
    """Normalize outputs for stable comparison."""
    if isinstance(value, float):
        return round(value, 8)
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return [normalize(v) for v in value]
    return value


def diff_traces(trace_a: dict, trace_b: dict) -> list[dict]:
    """Compare two execution traces."""
    diffs = []
    nodes_a = {n["name"]: n for n in trace_a.get("nodes", [])}
    nodes_b = {n["name"]: n for n in trace_b.get("nodes", [])}

    all_nodes = set(nodes_a) | set(nodes_b)

    for name in sorted(all_nodes):
        a = nodes_a.get(name)
        b = nodes_b.get(name)

        if not a or not b:
            diffs.append({"node": name, "type": "added_or_removed"})
            continue

        if normalize(a["output"]) != normalize(b["output"]):
            diffs.append(
                {
                    "node": name,
                    "type": "output_diff",
                    "expected": a["output"],
                    "actual": b["output"],
                }
            )

    return diffs
