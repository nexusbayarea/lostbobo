#!/bin/bash
set -e
echo "=== Step 5 Validation ==="

TOKEN=$(curl -s -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo "Token obtained: ${TOKEN:0:20}..."

echo -n "Auth required: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/v1/rag/retrieve \
  -X POST -H "Content-Type: application/json" \
  -d '{"query":"test"}' | grep -q "401" && echo "OK (401 without token)" || echo "FAIL"

echo -n "Auth valid: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/v1/rag/retrieve \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"test"}' | grep -q "200" && echo "OK (200 with token)" || echo "FAIL"

echo "=== Step 5 Complete ==="
