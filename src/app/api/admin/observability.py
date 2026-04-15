from fastapi import APIRouter
from pathlib import Path
import json
import subprocess

router = APIRouter()

TRACE_FILE = Path(__file__).resolve().parents[5] / "runtime_trace.json"


@router.get("/admin/observability")
def get_trace():
    if not TRACE_FILE.exists():
        return {"status": "no data"}

    return json.loads(TRACE_FILE.read_text())


@router.post("/admin/replay")
def replay_failed():
    subprocess.Popen(["python", "tools/runtime/replay.py"])
    return {"status": "started"}


@router.post("/admin/replay/full")
def replay_full():
    subprocess.Popen(["python", "tools/runtime/replay.py", "full"])
    return {"status": "started"}
