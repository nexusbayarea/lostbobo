import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def bootstrap():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    # ensure deterministic import root
