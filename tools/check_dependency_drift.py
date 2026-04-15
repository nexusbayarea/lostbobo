"""
Dependency drift check.
Validates that the environment can boot and import core modules.
"""
import os
import sys
import importlib

def check_drift():
    module_name = os.getenv("DRIFT_TEST_IMPORT", "app.core.config")
    print(f"Checking dependency drift by importing: {module_name}")
    try:
        importlib.import_module(module_name)
        print(f"✅ Successfully imported {module_name}")
    except ImportError as e:
        print(f"❌ Failed to import {module_name}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error during import of {module_name}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_drift()
