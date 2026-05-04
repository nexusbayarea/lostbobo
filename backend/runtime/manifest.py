MANIFEST = {
    "version": "v3.5.1",
    "nodes": {
        "lint": {"type": "ci", "depends_on": []},
        "lockfile": {"type": "ci", "depends_on": ["lint"]},
        "pruning": {"type": "ci", "depends_on": ["lint"]},
        "boundaries": {"type": "ci", "depends_on": ["lockfile"]},
        "api": {"type": "ci", "depends_on": ["boundaries", "pruning"]},
    },
}


def load_manifest():
    return MANIFEST
