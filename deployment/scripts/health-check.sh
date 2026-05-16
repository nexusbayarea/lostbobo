#!/bin/bash
# Run on RunPod to verify all services are healthy.
set -e

echo "=== SimHPC Health Check ==="

echo -n "Redis: "
docker exec simhpc-redis redis-cli ping 2>/dev/null && echo "OK" || echo "FAIL"

echo -n "Ollama: "
curl -s http://localhost:11434/api/tags > /dev/null 2>&1 && echo "OK" || echo "FAIL"

echo -n "Gateway: "
curl -s http://localhost:8080/health 2>/dev/null | grep -q "ok" && echo "OK" || echo "FAIL"

echo -n "RAG Service: "
python3 -c "import grpc; ch = grpc.insecure_channel('localhost:50051'); grpc.channel_ready_future(ch).result(timeout=5); print('OK')" 2>/dev/null || echo "FAIL"

echo -n "Module Runtime: "
python3 -c "import grpc; ch = grpc.insecure_channel('localhost:50052'); grpc.channel_ready_future(ch).result(timeout=5); print('OK')" 2>/dev/null || echo "FAIL"

echo "=== Health Check Complete ==="
