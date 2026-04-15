import sys
import subprocess


def run_step(name: str, cmd: list) -> None:
    print(f"[Bootstrap] -> {name}")
    result = subprocess.run(cmd)

    if result.returncode != 0:
        print(f"[FAIL] {name}")
        sys.exit(result.returncode)

    print(f"[PASS] {name}")


def main(mode: str = "ci") -> None:
    run_step(
        "Kernel Boot",
        [sys.executable, "tools/runtime/kernel.py"],
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
