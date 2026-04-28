import subprocess
from pathlib import Path

ROOT = Path("backend")


def get_changed_files():
    # Use origin/main as baseline
    result = subprocess.run(
        ["git", "diff", "--name-only", "origin/main...HEAD"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip().splitlines()


def map_to_modules(files):
    modules = set()

    for f in files:
        parts = Path(f).parts
        if "backend" in parts:
            idx = parts.index("backend")
            if len(parts) > idx + 1:
                modules.add(parts[idx + 1])

    return modules


if __name__ == "__main__":
    files = get_changed_files()
    modules = map_to_modules(files)

    print(",".join(sorted(modules)))
