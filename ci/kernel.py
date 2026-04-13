#!/usr/bin/env python3
"""CI Kernel - single execution entry point."""

import subprocess
import sys

DEFAULT_MODULES = ["core", "api", "worker", "autoscaler", "tests"]


def run(cmd: str) -> int:
    return subprocess.run(cmd, shell=True).returncode


def main():
    print("CI Kernel Starting")

    modules = DEFAULT_MODULES
    print(f"Modules: {modules}")

    print("Running lint...")
    if run("ruff check . --fix") != 0:
        print("Lint failed")
        sys.exit(1)

    print("Lint OK")

    print("Running tests...")
    if run("pytest") != 0:
        print("Tests failed")
        sys.exit(1)

    print("Tests OK")

    print("CI Kernel Complete")


if __name__ == "__main__":
    main()
