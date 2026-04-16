#!/usr/bin/env python3
"""
SimHPC Master Bootstrap (v3.0.0 Beta Foundation)
Single Source of Truth for system validation and deterministic DAG execution.
"""
import sys
from pathlib import Path

# 1. Universal Path Resolution (Prevents ImportError regardless of execution context)
ROOT = Path(__file__).resolve().parents[1] 
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def verify_dependencies() -> bool:
    """Gate 1: Ensure local environment matches the uv.lock fingerprint"""
    try:
        # Attempt to use the precise fingerprint scanner
        from tools.deps.fingerprint import verify_fingerprint
        return verify_fingerprint()
    except ImportError:
        # Fallback to the legacy lock validator during the directory cleanup transition
        print("⚠️ [BOOTSTRAP] tools.deps.fingerprint missing. Trying legacy deps.py fallback...")
        try:
            from tools.runtime import deps
            return deps.validate_lock()
        except ImportError:
            print("❌ [BOOTSTRAP] Critical dependency validation missing.")
            return False

def bootstrap() -> int:
    print("🚀 [BOOTSTRAP] Initiating SimHPC LBA Validation Sequence...")

    # Gate 1: Dependency Integrity
    if not verify_dependencies():
        print("❌ [BOOTSTRAP] Dependency Drift Detected. Run 'uv sync'.")
        return 1
    print("✅ [BOOTSTRAP] Dependency fingerprint verified.")

    # Gate 2: System Contract Validation (Registry)
    from tools.registry import validate as validate_registry
    print("🔍 [BOOTSTRAP] Validating system module map...")
    try:
        validate_registry()
        print("✅ [BOOTSTRAP] Module contract validated.")
    except ImportError as e:
        print(f"❌ [BOOTSTRAP] Contract validation failed: {e}")
        return 1

    # Gate 3: Deterministic Graph Execution
    print("⚙️ [BOOTSTRAP] Executing Deterministic CI Graph...")
    try:
        from tools.runtime.nodes import register_default_nodes
        from tools.runtime.graph import GRAPH

        register_default_nodes()
        order = GRAPH.topologically_sorted()

        for node_id in order:
            node = GRAPH.get(node_id)
            print(f"  → [CI] Executing {node_id}...")
            
            # Execute the node function
            rc = node.fn({})
            
            if rc != 0:
                print(f"❌ [CI FAIL] Node '{node_id}' returned exit code {rc}")
                return rc

        print("✅ [CI PASS] All deterministic gates cleared.")
        return 0

    except Exception as e:
        print(f"❌ [BOOTSTRAP] Graph execution encountered a fatal error: {e}")
        return 1

def main():
    raise SystemExit(bootstrap())

if __name__ == "__main__":
    main()
