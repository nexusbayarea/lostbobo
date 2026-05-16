"""
SimHPC Kernel — orchestrator, gateway, capability registry, scheduler.
Edge API on :8080 (REST), internal gRPC on :50054.
"""

import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import grpc
import httpx
import redis.asyncio as aioredis
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

from services.proto import rag_pb2, rag_pb2_grpc, plugin_host_pb2, plugin_host_pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kernel")

RAG_HOST = os.getenv("RAG_SERVICE_HOST", "rag-service")
RAG_PORT = os.getenv("RAG_SERVICE_PORT", "50051")
MODULE_HOST = os.getenv("MODULE_RUNTIME_HOST", "module-runtime")
MODULE_PORT = os.getenv("MODULE_RUNTIME_PORT", "50052")
GPU_HOST = os.getenv("GPU_WORKER_HOST", "gpu-worker")
GPU_PORT = os.getenv("GPU_WORKER_PORT", "50053")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


class ServiceClients:
    def __init__(self):
        self.rag_stub: Optional[rag_pb2_grpc.RAGServiceStub] = None
        self.plugin_stub: Optional[plugin_host_pb2_grpc.PluginHostStub] = None
        self.redis: Optional[aioredis.Redis] = None
        self.deepseek: Optional[httpx.AsyncClient] = None

    async def connect(self):
        rag_channel = grpc.aio.insecure_channel(f"{RAG_HOST}:{RAG_PORT}")
        self.rag_stub = rag_pb2_grpc.RAGServiceStub(rag_channel)
        plugin_channel = grpc.aio.insecure_channel(f"{MODULE_HOST}:{MODULE_PORT}")
        self.plugin_stub = plugin_host_pb2_grpc.PluginHostStub(plugin_channel)
        self.redis = await aioredis.from_url(REDIS_URL)
        if DEEPSEEK_API_KEY:
            self.deepseek = httpx.AsyncClient(
                base_url="https://api.deepseek.com/v1",
                headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
                timeout=120.0,
            )

    async def close(self):
        if self.deepseek:
            await self.deepseek.aclose()


clients = ServiceClients()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await clients.connect()
    logger.info("Kernel started, services connected")
    yield
    await clients.close()


app = FastAPI(title="SimHPC Gamma Kernel", version="1.0.0", lifespan=lifespan)


async def verify_token(authorization: str = Header(None)) -> dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.replace("Bearer ", "")
    try:
        from jose import jwt

        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 5
    tenant_id: str = "default"


class ReasonRequest(BaseModel):
    context: list[dict]
    prompt_template: str = ""
    model: str = "deepseek-chat"


class IndexRequest(BaseModel):
    text: str
    metadata: dict = {}
    tenant_id: str = "default"


class GraphQueryRequest(BaseModel):
    query_type: str = "traverse"
    start_node: str = ""
    max_depth: int = 3
    tenant_id: str = "default"


class AgentLoopRequest(BaseModel):
    query: str
    max_steps: int = 3
    tenant_id: str = "default"


class SimulateRequest(BaseModel):
    capability: str
    payload: dict
    tenant_id: str = "default"
    priority: str = "normal"


class AuthRequest(BaseModel):
    username: str
    password: str


class EventRequest(BaseModel):
    event_type: str
    payload: dict


@app.post("/auth/token")
async def auth_token(req: AuthRequest):
    if ENVIRONMENT == "development":
        from jose import jwt

        payload = {"sub": req.username, "tenant_id": "default", "role": "admin"}
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return {"token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.get("/metrics")
async def metrics():
    return {
        "kernel_uptime": "running",
        "connected_services": ["rag", "module-runtime", "redis"],
    }


@app.get("/api/v1/test/ollama")
async def test_ollama():
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": "gemma:2b", "prompt": "Hello", "stream": False},
            timeout=30.0,
        )
        return resp.json()


@app.get("/api/v1/plugins")
async def list_plugins(user=Depends(verify_token)):
    resp = await clients.plugin_stub.HealthCheck(plugin_host_pb2.HealthRequest())
    return {"plugins": list(resp.plugins)}


@app.post("/api/v1/events/test")
async def emit_event(req: EventRequest, user=Depends(verify_token)):
    event = {
        "event_type": req.event_type,
        "payload": req.payload,
        "timestamp": datetime.utcnow().isoformat(),
        "tenant_id": user.get("tenant_id", "default"),
    }
    await clients.redis.xadd("events:hallucination", event, maxlen=1000)
    return {"status": "emitted", "event": event["event_type"]}


@app.post("/api/v1/rag/retrieve")
async def retrieve(req: RetrieveRequest, user=Depends(verify_token)):
    grpc_req = rag_pb2.RetrieveRequest(
        query=req.query, top_k=req.top_k, tenant_id=req.tenant_id
    )
    resp = await clients.rag_stub.Retrieve(grpc_req)
    return {
        "documents": [
            {"text": d.text, "score": d.score, "metadata": dict(d.metadata)}
            for d in resp.documents
        ]
    }


@app.post("/api/v1/rag/reason")
async def reason(req: ReasonRequest, user=Depends(verify_token)):
    if clients.deepseek and req.model == "deepseek-chat":
        context_text = "\n".join([d.get("text", "") for d in req.context])
        prompt = f"{req.prompt_template}\nContext:\n{context_text}"
        resp = await clients.deepseek.post(
            "/chat/completions",
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        data = resp.json()
        return {"answer": data["choices"][0]["message"]["content"]}
    grpc_req = rag_pb2.ReasonRequest(
        context=[rag_pb2.Document(text=d.get("text", "")) for d in req.context],
        prompt_template=req.prompt_template,
        model=req.model,
    )
    resp = await clients.rag_stub.Reason(grpc_req)
    return {"answer": resp.answer}


@app.post("/api/v1/rag/index")
async def index_document(req: IndexRequest, user=Depends(verify_token)):
    grpc_req = rag_pb2.IndexRequest(
        text=req.text, metadata=req.metadata, tenant_id=req.tenant_id
    )
    resp = await clients.rag_stub.Index(grpc_req)
    return {"success": resp.success}


@app.post("/api/v1/rag/graph-query")
async def graph_query(req: GraphQueryRequest, user=Depends(verify_token)):
    grpc_req = rag_pb2.GraphQueryRequest(
        query_type=req.query_type,
        start_node=req.start_node,
        max_depth=req.max_depth,
        tenant_id=req.tenant_id,
    )
    resp = await clients.rag_stub.GraphQuery(grpc_req)
    return {
        "paths": [
            {"nodes": list(p.nodes), "relationship": p.relationship, "depth": p.depth}
            for p in resp.paths
        ]
    }


@app.post("/api/v1/rag/agent-loop")
async def agent_loop(req: AgentLoopRequest, user=Depends(verify_token)):
    grpc_req = rag_pb2.AgentLoopRequest(
        query=req.query, max_steps=req.max_steps, tenant_id=req.tenant_id
    )
    resp = await clients.rag_stub.AgentLoop(grpc_req)
    return {
        "final_answer": resp.final_answer,
        "steps": [{"step": s.step, "answer": s.answer} for s in resp.steps],
    }


@app.get("/api/v1/rag/stream")
async def stream_retrieve(
    query: str, tenant_id: str = "default", user=Depends(verify_token)
):
    async def event_generator():
        grpc_req = rag_pb2.StreamRetrieveRequest(query=query, tenant_id=tenant_id)
        async for chunk in clients.rag_stub.StreamRetrieve(grpc_req):
            docs = [{"text": d.text, "score": d.score} for d in chunk.documents]
            yield f"data: {json.dumps({'documents': docs})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/v1/simulate")
async def simulate(req: SimulateRequest, user=Depends(verify_token)):
    job_id = f"sim_{datetime.utcnow().timestamp()}"
    job = {
        "job_id": job_id,
        "capability": req.capability,
        "payload": req.payload,
        "tenant_id": req.tenant_id,
        "priority": req.priority,
        "user_id": user.get("sub"),
    }
    await clients.redis.lpush("queue:simulation", json.dumps(job))
    return {"job_id": job_id, "status": "queued"}


@app.get("/api/v1/simulate/{job_id}/status")
async def simulation_status(job_id: str, user=Depends(verify_token)):
    status = await clients.redis.get(f"job:{job_id}:status")
    return {"job_id": job_id, "status": status or "unknown"}


@app.post("/api/v1/plugins/{plugin_name}/execute")
async def execute_plugin(
    plugin_name: str, req: SimulateRequest, user=Depends(verify_token)
):
    grpc_req = plugin_host_pb2.ExecuteRequest(
        capability=req.capability,
        payload=req.payload,
        tenant_id=req.tenant_id,
    )
    resp = await clients.plugin_stub.ExecuteCapability(grpc_req)
    if resp.success:
        return {"result": resp.result}
    raise HTTPException(status_code=500, detail=resp.error)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False)
