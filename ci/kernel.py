#!/usr/bin/env python3
"""DAG Execution Engine with caching."""

import json
import os
import subprocess
import sys
from hash import compute_node_key


CACHE_PATH = ".cache/dag_cache.json"


def load_cache():
    """Load cache from disk."""
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {}


def save_cache(cache):
    """Persist cache to disk."""
    os.makedirs(".cache", exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


def run_node(image, node):
    """Execute a single DAG node."""
    entry = node.get("entry", f"ci/jobs/{node['name']}.py")
    print(f"Executing: {node['name']}")

    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{os.getcwd()}:/app",
            "-w",
            "/app",
            image,
            "python",
            entry,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"ERROR in {node['name']}:")
        print(result.stderr)
        sys.exit(1)

    print(f"OK: {node['name']}")
    return True


def main(manifest_path):
    """Main DAG execution loop."""
    manifest = json.load(open(manifest_path))
    image = manifest["image"]["ref"]
    image_digest = manifest["image"]["digest"]
    dag_jobs = manifest.get("dag", {}).get("jobs", [])

    print(f"Image: {image}")
    print(f"Digest: {image_digest}")
    print(f"Jobs: {len(dag_jobs)}")

    cache = load_cache()
    new_cache = {}

    for job in dag_jobs:
        job_name = job["name"]

        key = compute_node_key(job, cache, image_digest)

        if cache.get(job_name) == key:
            print(f"SKIP {job_name} (cache hit)")
            new_cache[job_name] = key
            continue

        print(f"RUN {job_name}")
        run_node(image, job)

        new_cache[job_name] = key

    save_cache(new_cache)
    print(f"Cache saved: {len(new_cache)} entries")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ci/kernel.py <manifest.json>")
        sys.exit(1)

    main(sys.argv[1])
