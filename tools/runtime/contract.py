from dataclasses import dataclass


@dataclass
class ExecutionContract:
    allowed_modules: set[str]
    forbidden_imports: set[str]
    entrypoints: set[str]


CONTRACT = ExecutionContract(
    allowed_modules={"app", "worker", "tools", "scripts", "tests"},
    forbidden_imports={"ci."},
    entrypoints={"app.api.kernel"},
)

import hashlib
import json


def compute_contract(node: dict, upstream_contracts: dict) -> str:
    """
    Deterministic hash of node definition, including dependency contracts.
    """
    payload = {
        "type": node["type"],
        "inputs": node.get("inputs", {}),
        "deps": {d: upstream_contracts.get(d) for d in node.get("deps", [])},
    }

    encoded = json.dumps(payload, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()
