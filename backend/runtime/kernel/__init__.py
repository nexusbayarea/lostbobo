import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Explicitly add backend to sys.path so 'runtime' is available
ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

# Use absolute imports relative to the backend package root
from runtime.compiler.ast_normalizer import normalize_file

class ExecutionKernel:
    """
    Kernel acts as a PURE MUTATION engine. 
    It performs normalization and structural fixes, 
    but NEVER validates results.
    """
    def execute(self):
        print("[KERNEL] Starting single-pass deterministic normalization")
        
        # 1. Structural Normalization
        print("[KERNEL] Normalizing AST...")
        for path in Path(BACKEND).rglob("*.py"):
            normalize_file(path)
            
        # 2. Single-Pass Mutation
        print("[KERNEL] Running Ruff formatting and structural fixes...")
        subprocess.run(["python", "-m", "ruff", "format", "backend"], check=True)
        subprocess.run(["python", "-m", "ruff", "check", "backend", "--fix", "--unsafe-fixes"], check=True)
        
        print("[KERNEL] Mutation complete. Passing to CI Validation.")
        return 0

if __name__ == "__main__":
    kernel = ExecutionKernel()
    raise SystemExit(kernel.execute())
