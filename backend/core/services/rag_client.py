from __future__ import annotations

from typing import Any


class CoreRAGClient:
    def __init__(self, host: str = "localhost", port: int = 50051):
        self.host = host
        self.port = port
        self._channel = None
        self._stub = None

    async def _ensure_connected(self) -> None:
        if self._stub is not None:
            return
        try:
            import grpc
            from services.rag.proto import rag_pb2_grpc

            self._channel = grpc.aio.insecure_channel(f"{self.host}:{self.port}")
            self._stub = rag_pb2_grpc.RAGServiceStub(self._channel)
        except ImportError:
            self._stub = None

    async def retrieve(self, payload: dict[str, Any]) -> dict[str, Any]:
        await self._ensure_connected()
        if self._stub is None:
            return {
                "documents": [
                    {
                        "text": "Core RAG service not available (gRPC stub not loaded). "
                        "Install grpcio and generate proto stubs.",
                        "score": 0.0,
                        "metadata": {},
                    }
                ]
            }
        try:
            from services.rag.proto import rag_pb2

            request = rag_pb2.RetrieveRequest(
                query=payload["query"],
                top_k=payload.get("top_k", 5),
            )
            response = await self._stub.Retrieve(request)
            return {
                "documents": [
                    {
                        "text": d.text,
                        "score": d.score,
                        "metadata": dict(d.metadata),
                    }
                    for d in response.documents
                ]
            }
        except Exception as e:
            return {"documents": [], "error": str(e)}

    async def reason(self, payload: dict[str, Any]) -> dict[str, Any]:
        await self._ensure_connected()
        if self._stub is None:
            return {"answer": "Core RAG service not available."}
        try:
            from services.rag.proto import rag_pb2

            context = [
                rag_pb2.Document(text=doc["text"], metadata=doc.get("metadata", {}))
                for doc in payload.get("context", [])
            ]
            request = rag_pb2.ReasonRequest(
                context=context,
                prompt_template=payload.get("prompt_template", ""),
                model=payload.get("model", "gpt-4"),
            )
            response = await self._stub.Reason(request)
            return {"answer": response.answer}
        except Exception as e:
            return {"answer": "", "error": str(e)}

    async def index(self, payload: dict[str, Any]) -> dict[str, Any]:
        await self._ensure_connected()
        if self._stub is None:
            return {"success": False, "error": "gRPC stub not loaded"}
        try:
            from services.rag.proto import rag_pb2

            request = rag_pb2.IndexRequest(
                text=payload["text"],
                metadata=payload.get("metadata", {}),
            )
            response = await self._stub.Index(request)
            return {"success": response.success}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def close(self) -> None:
        if self._channel:
            await self._channel.close()
