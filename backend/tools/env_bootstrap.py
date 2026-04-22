import platform
import json
import subprocess
import sys
from pathlib import Path


def run(cmd: str, cwd: Path = None):
    print(f"[ENV] {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if result.returncode != 0:
        sys.exit(result.returncode)


def main(mode="dev"):
    print(f"[ENV] Bootstrap mode: {mode}")

    run("python -m pip install --upgrade pip")

    run("pip install -r requirements.api.lock")

    if mode in ("dev", "ci"):
        run("pip install -r requirements.dev.lock")

    run("pip install -e .")

    print("[ENV] bootstrap complete")

    print(json.dumps({
        "python": platform.python_version(),
        "os": platform.system(),
    }))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "dev"
    main(mode)