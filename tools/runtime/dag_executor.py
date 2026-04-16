import sys
from pathlib import Path
import subprocess


def load_manifest() -> dict:
    path = Path("tools/ci_manifest.yml")
    if not path.exists():
        raise FileNotFoundError("tools/ci_manifest.yml missing")

    import yaml

    return yaml.safe_load(path.read_text())


def run_node(node: dict) -> int:
    path = node.get("path", "")
    if not path or not Path(path).exists():
        print(f"[DAG] missing node: {path}")
        return 1

    print(f"[DAG] Running: {node.get('name', path)}")
    result = subprocess.run([sys.executable, path])
    return result.returncode


def topological_run(manifest: dict) -> int:
    nodes = manifest.get("nodes", {})
    executed = set()

    def execute(name: str) -> int:
        if name in executed:
            return 0

        node = nodes.get(name, {})

        for dep in node.get("depends_on", []):
            if execute(dep) != 0:
                return 1

        rc = run_node(node)
        executed.add(name)
        return rc

    for node_name in nodes:
        if execute(node_name) != 0:
            return 1

    return 0


def main():
    manifest = load_manifest()
    sys.exit(topological_run(manifest))


if __name__ == "__main__":
    main()
