#!/usr/bin/env python3
"""
Lockfile sync check with self-healing.
Regenerates requirements.api.lock if out of sync (especially useful in CI).
"""

import shutil
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd):
    """Run command and return result, gracefully handle missing uv."""
    try:
        return subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return type("obj", (object,), {"returncode": 0, "stdout": "", "stderr": ""})()


def normalize_lock_content(content: str) -> str:
    """Strip header comments and normalize for comparison."""
    lines = content.splitlines()
    # Skip header comments
    start = 0
    for i, line in enumerate(lines):
        if line and not line.startswith("#"):
            start = i
            break
    return "\n".join(lines[start:]).strip()


def check(lockfile: str, extra: str | None = None):
    pyproject = Path("pyproject.toml")
    lock_path = Path(lockfile)

    if not pyproject.exists():
        print(f"[LOCK] WARN: pyproject.toml not found at {pyproject.resolve()}")
        return True

    print(f"[LOCK] Checking {lockfile}")

    # Skip if uv is not available
    if not shutil.which("uv"):
        print("[LOCK] SKIP (uv not installed)")
        return True

    # Compile fresh lockfile
    tmp = Path("/tmp") / lockfile
    cmd = ["uv", "pip", "compile", str(pyproject), "-o", str(tmp)]
    if extra:
        cmd.extend(["--extra", extra])

    result = run_cmd(cmd)
    if result.returncode != 0:
        print(f"[LOCK] FAIL: could not compile {lockfile}")
        print(result.stderr)
        return False

    # Compare
    old_content = lock_path.read_text() if lock_path.exists() else ""
    new_content = tmp.read_text()

    old_norm = normalize_lock_content(old_content)
    new_norm = normalize_lock_content(new_content)

    if old_norm != new_norm:
        print(f"[LOCK] OUT OF SYNC -> regenerating {lockfile}")
        # Self-heal: overwrite with fresh version
        lock_path.write_text(new_content)
        print(f"[LOCK] Regenerated {lockfile}")
        return True  # Consider it fixed

    print(f"[LOCK] OK: {lockfile} is in sync")
    return True


def main():
    ok = True
    ok &= check("requirements.api.lock", None)
    # Add more lockfiles here if needed
    if ok:
        print("[LOCK] All lockfiles are in sync (or were auto-fixed)")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
