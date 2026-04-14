import json
from pathlib import Path

STORE_PATH = Path(".ci/failures.json")

def load():
    if not STORE_PATH.exists():
        return []
    return json.loads(STORE_PATH.read_text())

def save(data):
    STORE_PATH.parent.mkdir(exist_ok=True, parents=True)
    STORE_PATH.write_text(json.dumps(data, indent=2))

def record(fingerprint, fix, success):
    data = load()

    data.append({
        "fingerprint": fingerprint,
        "fix": fix,
        "success": success
    })

    save(data)
