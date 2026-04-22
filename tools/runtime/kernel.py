import subprocess
import json


STAGES = [
    {
        "name": "import_fix",
        "cmd": "python -m ruff check . --select I --fix",
        "category": "IMPORTS",
    },
    {
        "name": "format",
        "cmd": "python -m ruff format .",
        "category": "FORMAT",
    },
    {
        "name": "typing_fix",
        "cmd": "python -m ruff check . --select UP --fix",
        "category": "TYPING",
    },
    {
        "name": "strict_lint",
        "cmd": "python -m ruff check .",
        "category": "STRICT",
    },
]


def run_stage(stage):
    print(f"\n[KERNEL] Running {stage['name']}")

    result = subprocess.run(stage["cmd"], shell=True)

    return {
        "stage": stage["name"],
        "category": stage["category"],
        "code": result.returncode,
    }


def run_kernel():
    trace = []

    print("[KERNEL] boot sequence start")

    for stage in STAGES:
        result = run_stage(stage)
        trace.append(result)

        # STRICT FAILURE ONLY AT END
        if stage["name"] == "strict_lint" and result["code"] != 0:
            print("[KERNEL] FAILED at strict gate")
            break

    with open("ci_trace.json", "w") as f:
        json.dump(trace, f, indent=2)

    if trace[-1]["code"] == 0:
        print("\n[KERNEL] SUCCESS - system converged")
        return 0

    print("\n[KERNEL] FAILED - non-converged state")
    return 1


if __name__ == "__main__":
    raise SystemExit(run_kernel())
