"""
CI Runtime Mode entry point.
"""
import sys
import os

def main():
    mode = os.getenv("RUNTIME_MODE", "ci")
    print(f"--- SimHPC CI Runtime Test ---")
    
    # Import and run boot DAG
    try:
        from app.core.runtime.boot import run_boot_dag
        success = run_boot_dag(mode)
        if success:
            print("CI Runtime Validation Successful!")
            sys.exit(0)
        else:
            print("CI Runtime Validation Failed!")
            sys.exit(1)
    except Exception as e:
        print(f"Fatal error booting in CI mode: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
