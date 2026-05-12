from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.core.execution.streaming import SimulationEvent

router = APIRouter(prefix="/api/v1/worker", tags=["worker"])


class WorkerRegistrationRequest(BaseModel):
    worker_id: str
    capabilities: dict


class WorkerResult(BaseModel):
    execution_id: str
    status: str
    output: dict = {}


class TelemetryEvent(BaseModel):
    worker_id: str
    execution_id: str
    event_type: str
    timestamp: float
    data: dict


def get_kernel(request):
    return request.app.state.kernel


KernelDep = Depends(get_kernel)


@router.post("/register")
async def worker_register(req: WorkerRegistrationRequest, kernel=KernelDep):
    from backend.core.workers.registration import WorkerCapabilities

    info = WorkerCapabilities(worker_id=req.worker_id, capabilities=req.capabilities)
    await kernel.capabilities.invoke("worker.register", info.__dict__)
    return {"status": "registered", "worker_id": req.worker_id}


@router.get("/dequeue")
async def dequeue_job(kernel=KernelDep):
    job = await kernel.execution_queue.dequeue()
    if job is None:
        raise HTTPException(status_code=204)
    return job.model_dump()


@router.post("/result")
async def post_result(result: WorkerResult, kernel=KernelDep):
    await kernel.capabilities.invoke("execution.complete", result.model_dump())
    return {"ack": True}


@router.post("/telemetry")
async def post_telemetry(event: TelemetryEvent, kernel=KernelDep):
    sim_event = SimulationEvent(
        execution_id=event.execution_id,
        event_type=event.event_type,
        data=event.data,
    )
    await kernel.stream_mgr.push_event(event.execution_id, sim_event)
    return {"ack": True}
