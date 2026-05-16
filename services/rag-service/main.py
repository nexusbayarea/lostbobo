"""
Core RAG Service — gRPC server for retrieval, GraphRAG, agentic RAG.
Vector queries via Supabase pgvector. Reasoning via DeepSeek (no local Ollama).
"""

import asyncio
import json
import logging
import os
from concurrent import futures

import grpc
import numpy as np
import httpx
from supabase import create_client, Client

from services.proto import rag_pb2, rag_pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rag-service")

VECTOR_DIM = int(os.getenv("VECTOR_DIM", "768"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE = "https://api.deepseek.com/v1"


class DeepSeekClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=DEEPSEEK_BASE,
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            timeout=60.0,
        )

    async def embed(self, text: str | list[str]) -> np.ndarray:
        if isinstance(text, str):
            texts = [text]
        else:
            texts = text
        response = await self.client.post(
            "/embeddings",
            json={
                "model": "text-embedding-ada-002",
                "input": texts,
            },
        )
        response.raise_for_status()
        data = response.json()
        embeddings = np.array([d["embedding"] for d in data["data"]], dtype=np.float32)
        return embeddings[0] if isinstance(text, str) else embeddings

    async def generate(self, prompt: str, model: str = "deepseek-chat") -> str:
        response = await self.client.post(
            "/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


class PgVectorStore:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def search(
        self, embedding: np.ndarray, top_k: int = 5, tenant_id: str = None
    ) -> list[dict]:
        query = self.supabase.rpc(
            "match_documents",
            {
                "query_embedding": embedding.tolist(),
                "match_count": top_k,
                "filter_tenant": tenant_id,
            },
        )
        response = await query.execute()
        return response.data or []

    async def insert(
        self, content: str, embedding: np.ndarray, tenant_id: str, metadata: dict = None
    ):
        await (
            self.supabase.table("rag_documents")
            .insert(
                {
                    "content": content,
                    "embedding": embedding.tolist(),
                    "tenant_id": tenant_id,
                    "metadata": metadata or {},
                }
            )
            .execute()
        )

    async def graph_traverse(
        self, tenant_id: str, start_node: str, max_depth: int = 3
    ) -> list[dict]:
        """BFS traversal using Supabase graph_nodes and graph_edges tables."""
        visited = {start_node}
        queue = [(start_node, 0, [start_node])]
        paths = []
        while queue:
            node, depth, path = queue.pop(0)
            if depth >= max_depth:
                continue
            edges = (
                await self.supabase.table("graph_edges")
                .select("*")
                .eq("tenant_id", tenant_id)
                .eq("source_node_id", node)
                .execute()
            )
            for edge in edges.data or []:
                target = edge["target_node_id"]
                if target not in visited:
                    visited.add(target)
                    new_path = path + [target]
                    paths.append(
                        {
                            "path": new_path,
                            "relationship": edge["relationship"],
                            "depth": depth + 1,
                        }
                    )
                    queue.append((target, depth + 1, new_path))
        return paths


class AgenticRAG:
    def __init__(self, vector_store, deepseek: DeepSeekClient):
        self.vector_store = vector_store
        self.deepseek = deepseek

    async def run(self, query: str, tenant_id: str, max_steps: int = 3) -> dict:
        memory = []
        current_query = query
        for step in range(max_steps):
            embedding = await self.deepseek.embed(current_query)
            docs = await self.vector_store.search(
                embedding, top_k=5, tenant_id=tenant_id
            )
            context = "\n".join([d["content"] for d in docs])
            prompt = (
                f"Question: {current_query}\nContext:\n{context}\n\nAnswer concisely:"
            )
            answer = await self.deepseek.generate(prompt)
            memory.append(
                {
                    "step": step,
                    "query": current_query,
                    "answer": answer,
                    "docs": len(docs),
                }
            )
            if "final" in answer.lower() or step == max_steps - 1:
                break
            current_query = f"Further details about: {answer[:200]}"
        return {"final_answer": memory[-1]["answer"], "trail": memory}


class RAGServiceServicer(rag_pb2_grpc.RAGServiceServicer):
    def __init__(self):
        self.deepseek = DeepSeekClient()
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.vector_store = PgVectorStore(self.supabase)
        self.agentic_rag = AgenticRAG(self.vector_store, self.deepseek)

    async def Retrieve(self, request, context):
        embedding = await self.deepseek.embed(request.query)
        docs = await self.vector_store.search(
            embedding, top_k=request.top_k, tenant_id=request.tenant_id
        )
        response = rag_pb2.RetrieveResponse()
        for doc in docs:
            md = doc.get("metadata", {})
            if isinstance(md, str):
                try:
                    md = json.loads(md)
                except (json.JSONDecodeError, TypeError):
                    md = {}
            response.documents.add(
                text=doc.get("content", ""),
                score=doc.get("similarity", 0.0),
                metadata=md,
            )
        return response

    async def Reason(self, request, context):
        context_text = "\n".join([d.text for d in request.context])
        prompt = (
            f"{request.prompt_template}\nContext:\n{context_text}"
            if context_text
            else request.prompt_template
        )
        answer = await self.deepseek.generate(prompt, request.model or "deepseek-chat")
        return rag_pb2.ReasonResponse(answer=answer)

    async def Index(self, request, context):
        embedding = await self.deepseek.embed(request.text)
        await self.vector_store.insert(
            request.text, embedding, request.tenant_id, dict(request.metadata)
        )
        return rag_pb2.IndexResponse(success=True)

    async def GraphQuery(self, request, context):
        if request.query_type == "traverse":
            paths = await self.vector_store.graph_traverse(
                request.tenant_id, request.start_node, request.max_depth
            )
            response = rag_pb2.GraphQueryResponse()
            for p in paths:
                response.paths.add(
                    nodes=p["path"], relationship=p["relationship"], depth=p["depth"]
                )
            return response
        return rag_pb2.GraphQueryResponse()

    async def AgentLoop(self, request, context):
        result = await self.agentic_rag.run(
            request.query, request.tenant_id, request.max_steps
        )
        response = rag_pb2.AgentLoopResponse()
        response.final_answer = result["final_answer"]
        for step in result["trail"]:
            response.steps.add(step=step["step"], answer=step["answer"])
        return response

    async def StreamRetrieve(self, request, context):
        embedding = await self.deepseek.embed(request.query)
        for batch_size in [3, 5, 10]:
            docs = await self.vector_store.search(
                embedding, top_k=batch_size, tenant_id=request.tenant_id
            )
            chunk = rag_pb2.StreamChunk()
            for doc in docs:
                md = doc.get("metadata", {})
                if isinstance(md, str):
                    try:
                        md = json.loads(md)
                    except (json.JSONDecodeError, TypeError):
                        md = {}
                chunk.documents.add(
                    text=doc.get("content", ""), score=doc.get("similarity", 0.0)
                )
            yield chunk


async def serve():
    port = os.getenv("PORT", "50051")
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=20))
    servicer = RAGServiceServicer()
    rag_pb2_grpc.add_RAGServiceServicer_to_server(servicer, server)
    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    logger.info(f"RAG Service listening on port {port}")
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
