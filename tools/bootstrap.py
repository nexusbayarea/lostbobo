import subprocess
import sys


def run_step(name: str, cmd: list[str]) -> None:
    print(f"[Bootstrap] -> {name}")
    result = subprocess.run(cmd)

    if result.returncode != 0:
        print(f"[FAIL] {name}")
        sys.exit(result.returncode)

    print(f"[PASS] {name}")


def dependency_healing_phase():
    print("[BOOTSTRAP] Dependency Healing Phase")

    project_files = [
        "tools/bootstrap.py",
        "tools/runtime/dag_executor.py",
        "tools/ci_gates/system_contract.py",
    ]

    result = subprocess.run(
        ["python", "tools/deps/self_heal_deps.py"],
        input="\n".join(project_files),
        text=True,
    )

    if result.returncode != 0:
        print("[FAIL] Dependency Healing")
        sys.exit(result.returncode)

    print("[PASS] Dependency Healing")


def main(mode: str = "ci") -> None:
    dependency_healing_phase()

    run_step(
        "DAG Executor",
        ["python", "tools/runtime/dag_executor.py"],
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
