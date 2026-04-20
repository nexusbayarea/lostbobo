import json
from pathlib import Path

def record(node_id, contract, result, path):
    trace_file = Path(path) / f"{node_id}.json"
    with open(trace_file, "w") as f:
        json.dump({
            "contract": contract,
            "result": result
        }, f)

def load(node_id, path):
    trace_file = Path(path) / f"{node_id}.json"
    if not trace_file.exists():
        return None

    with open(trace_file) as f:
        return json.load(f)
