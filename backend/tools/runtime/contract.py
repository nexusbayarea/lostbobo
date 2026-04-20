import hashlib
import json

def compute_contract(node: dict) -> str:
    """
    Deterministic hash of node definition.
    """
    payload = {
        "type": node["type"],
        "inputs": node.get("inputs", {}),
    }

    encoded = json.dumps(payload, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()
