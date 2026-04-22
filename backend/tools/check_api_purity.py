import sys
from pathlib import Path

LOCKFILE = Path(__file__).resolve().parent.parent / "requirements.api.lock"
FORBIDDEN = ["numpy", "scipy", "torch"]

if not LOCKFILE.exists():
    print(f"Lockfile not found: {LOCKFILE}")
    sys.exit(1)

content = LOCKFILE.read_text()
violations = [pkg for pkg in FORBIDDEN if f"\n{pkg}==" in content]

if violations:
    print(f"API lock contaminated: {violations}")
    sys.exit(1)

print("API purity OK")
