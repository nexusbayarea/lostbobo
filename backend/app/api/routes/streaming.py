"""SSE Streaming Route — Real-time partial responses."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from backend.runtime.cpu_node.orchestrator import CPUNodeOrchestrator

router = APIRouter(prefix="/stream", tags=["streaming"])

cpu_orchestrator = CPUNodeOrchestrator()


async def event_generator(query: str) -> AsyncGenerator[str, None]:
    """Streams partial tokens + final result."""
    try:
        async for chunk in cpu_orchestrator.stream_evaluate(query):
            if isinstance(chunk, str):
                yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'complete', 'data': chunk})}\n\n"
    except asyncio.CancelledError:
        yield f"data: {json.dumps({'type': 'cancelled'})}\n\n"
    finally:
        yield "data: [DONE]\n\n"


@router.get("/query")
async def stream_query(request: Request, query: str) -> StreamingResponse:
    """SSE endpoint for real-time streaming."""
    return StreamingResponse(
        event_generator(query),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )
