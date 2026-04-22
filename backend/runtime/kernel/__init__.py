import os
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from runtime.compiler.ast_normalizer import normalize_file

# Set backend as canonical import root
ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

class ExecutionKernel:
    def __init__(self):
        self.run_id = datetime.utcnow().isoformat()
        self.trace = []
        self.violations = {}

    def count_violations(self):
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "backend"],
            capture_output=True, text=True
        )
        import re
        match = re.search(r"Found (\d+) error", result.stdout)
        return int(match.group(1)) if match else 0

    def run_stage(self, name, action):
        before = self.count_violations()
        print(f"[KERNEL] Starting {name}...")
        
        if callable(action):
            action()
        else:
            subprocess.run(action, shell=True)
            
        after = self.count_violations()
        self.trace.append({
            "stage": name,
            "before": before,
            "after": after,
            "delta": before - after
        })
        return after <= before

    def execute(self):
        stages = [
            ("AST Normalization", lambda: [normalize_file(p) for p in Path(BACKEND).rglob("*.py")]),
            ("Import Fix", "python -m ruff check backend --select I --fix"),
            ("Format", "python -m ruff format backend"),
            ("Typing Fix", "python -m ruff check backend --select UP --fix"),
            ("Unsafe Fixes", "python -m ruff check backend --fix --unsafe-fixes"),
        ]

        for name, action in stages:
            if not self.run_stage(name, action):
                print(f"[KERNEL] FAILED at {name}")
                return 1

        final = self.count_violations()
        output = {
            "run_id": self.run_id,
            "status": "SUCCESS" if final == 0 else "FAILED",
            "trace": self.trace,
            "final_violations": final
        }
        with open("ci_run_summary.json", "w") as f:
            json.dump(output, f, indent=2)
        
        return 0 if final == 0 else 1

if __name__ == "__main__":
    kernel = ExecutionKernel()
    raise SystemExit(kernel.execute())
