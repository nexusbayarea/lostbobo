#!/bin/bash
set -e
echo "=== Step 1 Validation ==="

echo -n "Redis: "
docker exec simhpc-redis redis-cli ping | grep -q PONG && echo "OK" || { echo "FAIL"; exit 1; }

echo -n "Ollama: "
curl -s http://localhost:11434/api/tags > /dev/null && echo "OK" || { echo "FAIL"; exit 1; }

echo -n "Gateway: "
curl -s http://localhost:8080/health | grep -q "ok" && echo "OK" || { echo "FAIL"; exit 1; }

echo "=== Step 1 Complete ==="
