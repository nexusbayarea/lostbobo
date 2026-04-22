import subprocess
import json
import time
import sys
import os
import glob
from datetime import datetime
from pathlib import Path
from tools.ci.dag import CI_DAG
from tools.ci.diff_engine import diff_runs
from tools.ci.root_cause import find_root_failure, infer_hint

TRACE = []
HISTORY_DIR = "ci_history"

os.makedirs(HISTORY_DIR, exist_ok=True)


def run_node(node, cwd=None):
    print(f"\n[TRACE] Running {node.get('name', node['id'])}")

    start = time.time()

    result = subprocess.run(
        node["cmd"],
        shell=True,
        capture_output=True,
        text=True,
        cwd=cwd,
    )

    duration = time.time() - start

    entry = {
        "node": node["id"],
        "name": node.get("name", node["id"]),
        "cmd": node["cmd"],
        "return_code": result.returncode,
        "stdout": result.stdout[-5000:] if result.stdout else "",
        "stderr": result.stderr[-5000:] if result.stderr else "",
        "duration": round(duration, 3),
        "status": "PASS" if result.returncode == 0 else "FAIL",
    }

    TRACE.append(entry)

    print(f"[TRACE] {entry['status']} - {entry['duration']}s")

    if result.returncode != 0:
        print(f"[TRACE] STDERR: {result.stderr[-1000:]}")
        return False

    return True


def get_last_success():
    """Find the last successful (all PASS) run in history."""
    files = sorted(glob.glob(f"{HISTORY_DIR}/*.json"))
    
    for f in reversed(files):
        with open(f) as fp:
            data = json.load(fp)
        
        if all(node["status"] == "PASS" for node in data):
            return data
    
    return None


def report_failure():
    """Generate diff report and root cause analysis on failure."""
    print("\n" + "=" * 50)
    print("[DIFF] Comparing with last successful run")
    print("=" * 50)
    
    prev = get_last_success()
    if prev:
        diff = diff_runs(prev, TRACE)
        for d in diff:
            marker = "❌" if d["changed"] else "✔"
            print(f"  {marker} {d['node']}: {d['prev']} -> {d['current']}")
    else:
        print("  No previous run found in history")
    
    print("\n" + "=" * 50)
    print("[ROOT CAUSE] Failure Analysis")
    print("=" * 50)
    
    root = find_root_failure(TRACE)
    if root:
        print(f"  Failed node: {root['root_node']}")
        print(f"  Error: {root['error'][:200]}")
        print(f"  Hint: {root['hint']}")
        if root.get("fix"):
            print(f"  Fix: {root['fix']}")
    else:
        print("  No root cause found")


def run_dag(cwd=None):
    for node in CI_DAG:
        success = run_node(node, cwd=cwd)
        if not success:
            print(f"\n[TRACE] FAILED at node: {node.get('name', node['id'])}")
            save_trace()
            save_history()
            report_failure()
            sys.exit(1)

    save_trace()
    save_history()
    print("\n[TRACE] CI completed successfully")
    return True


def save_trace(path="ci_trace.json"):
    with open(path, "w") as f:
        json.dump(TRACE, f, indent=2)
    print(f"[TRACE] Saved to {path}")


def save_history():
    """Save run to history with timestamp."""
    run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = f"{HISTORY_DIR}/{run_id}.json"
    with open(path, "w") as f:
        json.dump(TRACE, f, indent=2)
    print(f"[HISTORY] Saved to {path}")


def load_trace(path="ci_trace.json"):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return None


if __name__ == "__main__":
    try:
        run_dag()
    except Exception as e:
        save_trace()
        save_history()
        print(f"[TRACE] Exception: {e}")
        raise