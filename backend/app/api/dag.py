import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.runtime.dag_executor import execute_dag
from backend.runtime.graph import GRAPH

router = APIRouter(prefix="/dag", tags=["DAG"])


@router.get("/graph")
async def get_dag_graph():
    nodes = []
    for node_id, node in GRAPH.nodes.items():
        nodes.append(
            {
                "id": node_id,
                "type": node.metadata.get("type", "default"),
                "data": {
                    "label": node_id,
                    "gpu": node.metadata.get("gpu", False),
                    "status": "idle",
                },
                "position": {"x": 100 * (len(nodes) % 5), "y": 80 * (len(nodes) // 5)},
            }
        )

    edges = [
        {"id": f"e-{dep}-{nid}", "source": dep, "target": nid, "animated": True}
        for nid, node in GRAPH.nodes.items()
        for dep in node.deps
    ]

    return {"nodes": nodes, "edges": edges}


@router.post("/run/{node_id}")
async def run_specific_node(node_id: str):
    """Run a single node or full DAG."""
    if node_id == "full":
        trace = await execute_dag()
        return {"status": "success", "trace": trace.timestamp}

    node = GRAPH.get(node_id)
    result = await node.fn({"id": node_id}) if asyncio.iscoroutinefunction(node.fn) else node.fn({"id": node_id})
    return {"node": node_id, "result": result}


active_connections = []


@router.websocket("/ws")
async def dag_websocket(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for conn in active_connections:
                await conn.send_text(f"[{data}]")
    except WebSocketDisconnect:
        active_connections.remove(websocket)
