import os
import sys
from pathlib import Path

# Set the backend as the ONLY import root
ROOT = Path(__file__).resolve().parents[3] # C:\Users\arche\SimHPC
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

import subprocess
from runtime.compiler.ast_normalizer import normalize_file

def ensure_deps():
    print("[KERNEL] Ensuring dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "ruff"], check=True)

def normalize_source():
    print("[KERNEL] AST normalization stage")
    for path in Path(BACKEND).rglob("*.py"):
        normalize_file(path)

def run(cmd: str):
    print(f"[KERNEL] {cmd}")
    # Run with PYTHONPATH set to backend
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND)
    return subprocess.run(cmd, shell=True, env=env).returncode

def run_kernel():
    print("[KERNEL] boot sequence start")
    
    # 1. STRUCTURAL NORMALIZATION
    normalize_source()

    # 2. IMPORT FIX (safe)
    run("python -m ruff check backend --select I --fix")

    # 3. FORMAT
    run("python -m ruff format backend")

    # 4. TYPE MODERNIZATION
    run("python -m ruff check backend --select UP --fix")

    # 5. UNSAFE COMPLETION PASS
    run("python -m ruff check backend --fix --unsafe-fixes")

    # 6. FINAL STRICT VALIDATION
    code = run("python -m ruff check backend")

    if code != 0:
        print("[KERNEL] FAILED - non-converged state")
        return 1

    print("[KERNEL] SUCCESS - converged state")
    return 0

if __name__ == "__main__":
    ensure_deps()
    raise SystemExit(run_kernel())
