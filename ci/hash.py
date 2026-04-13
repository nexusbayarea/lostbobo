#!/usr/bin/env python3
"""HashEngine - compute content hashes for DAG cache."""

import hashlib
import os
import sys


def hash_files(paths):
    """Hash all files in paths recursively."""
    h = hashlib.sha256()

    for path in sorted(paths):
        if os.path.isfile(path):
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in sorted(files):
                    fp = os.path.join(root, file)
                    if os.path.isfile(fp):
                        with open(fp, "rb") as f:
                            for chunk in iter(lambda: f.read(8192), b""):
                                h.update(chunk)

    return h.hexdigest()


def hash_string(s):
    """Hash a single string."""
    return hashlib.sha256(s.encode()).hexdigest()


def compute_node_key(node, cache, image_digest):
    """Compute cache key for a node."""
    input_hash = hash_files(node.get("inputs", []))

    dep_keys = "".join(cache.get(dep, "") for dep in node.get("deps", []))

    combined = input_hash + dep_keys + image_digest
    return hash_string(combined)


def main():
    paths = sys.argv[1:] if len(sys.argv) > 1 else ["app/", "worker/", "packages/"]
    print(hash_files(paths))


if __name__ == "__main__":
    main()
