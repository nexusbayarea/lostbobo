from fastapi import APIRouter
from app.kernel.kernel import Kernel

router = APIRouter(prefix="/auto-research", tags=["auto-research"])

kernel = Kernel()


@router.post("/run")
async def run_research(payload: dict):
    return await kernel.execute({"type": "AUTO_RESEARCH_RUN", "payload": payload})
