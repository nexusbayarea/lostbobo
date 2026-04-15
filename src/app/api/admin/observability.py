from fastapi import APIRouter
from pathlib import Path
import json
from tools.runtime.contract import CONTRACT

router = APIRouter()

TRACE_FILE = CONTRACT.root / "runtime_trace.json"


@router.get("/admin/observability")
def get_trace():
    if not TRACE_FILE.exists():
        return {"status": "no data"}

    return json.loads(TRACE_FILE.read_text())
