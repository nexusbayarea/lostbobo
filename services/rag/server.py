"""
Core RAG Service — runs on a dedicated CPU node (RunPod).
Provides retrieval and reasoning capabilities to the kernel via gRPC.
"""

from __future__ import annotations

import asyncio
import logging
from concurrent import futures
from typing import Any

logger = logging.getLogger(__name__)

try:
    import grpc
    from services.rag.proto import rag_pb2, rag_pb2_grpc
except ImportError:
    grpc = None
    rag_pb2 = None
    rag_pb2_grpc = None


class RAGServiceServicer:
    def __init__(self, embedding_model=None, vector_store=None, llm_client=None):
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.llm_client = llm_client

    async def Retrieve(self, request, context) -> Any:
        if not rag_pb2:
            return self._empty_retrieve_response()
        from services.rag.proto import rag_pb2 as pb2

        response = pb2.RetrieveResponse()
        doc = response.documents.add()
        doc.text = f"Mock result for: {request.query}"
        doc.score = 0.95
        return response

    async def Reason(self, request, context) -> Any:
        if not rag_pb2:
            return self._empty_reason_response()
        from services.rag.proto import rag_pb2 as pb2

        return pb2.ReasonResponse(answer="Mock reasoning result.")

    async def Index(self, request, context) -> Any:
        if not rag_pb2:
            return self._empty_index_response()
        from services.rag.proto import rag_pb2 as pb2

        return pb2.IndexResponse(success=True)

    def _empty_retrieve_response(self):
        class MockDoc:
            text = ""
            score = 0.0
            metadata = {}

        class MockResponse:
            documents = [MockDoc()]

        return MockResponse()

    def _empty_reason_response(self):
        class MockResponse:
            answer = "Reasoning service not configured."

        return MockResponse()

    def _empty_index_response(self):
        class MockResponse:
            success = False

        return MockResponse()


async def serve(
    port: int = 50051,
    embedding_model=None,
    vector_store=None,
    llm_client=None,
) -> None:
    if grpc is None:
        logger.warning("grpcio not installed — RAG service cannot start")
        return

    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = RAGServiceServicer(
        embedding_model=embedding_model,
        vector_store=vector_store,
        llm_client=llm_client,
    )
    rag_pb2_grpc.add_RAGServiceServicer_to_server(servicer, server)
    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    logger.info("Core RAG Service listening on port %d", port)
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
