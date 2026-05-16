#!/bin/bash
echo "=== SSE Streaming Test ==="

TOKEN=$(curl -s -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])" 2>/dev/null || echo "")

if [ -z "$TOKEN" ]; then
  TOKEN="dev-token"
fi

curl -N -s http://localhost:8080/api/v1/rag/stream?query=test \
  -H "Authorization: Bearer $TOKEN" \
  | head -5

echo "=== Step 4 Complete ==="
