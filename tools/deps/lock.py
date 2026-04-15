import subprocess
import sys
from pathlib import Path


LOCK_FILE = Path("requirements.lock")
TMP_FILE = Path(".requirements.lock.tmp")


def generate_lock():
    result = subprocess.run(
        [
            "uv",
            "pip",
            "compile",
            "pyproject.toml",
            "-o",
            str(TMP_FILE),
            "--no-header",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("LOCK GENERATION FAILED")
        print(result.stderr)
        sys.exit(1)


def normalize(path: Path) -> str:
    lines = path.read_text().splitlines()
    cleaned = [
        line.strip()
        for line in lines
        if line.strip() and not line.startswith("#") and "==" in line
    ]
    return "\n".join(sorted(cleaned))


def verify():
    current = normalize(LOCK_FILE)
    generated = normalize(TMP_FILE)

    if current != generated:
        print("ZERO-DRIFT VIOLATION DETECTED")
        print("Run: python tools/deps/lock.py --write")
        sys.exit(1)


def write():
    TMP_FILE.replace(LOCK_FILE)


def main():
    generate_lock()

    if "--write" in sys.argv:
        write()
        print("LOCK UPDATED")
        return

    verify()
    print("LOCK STABLE")


if __name__ == "__main__":
    main()
