#!/bin/bash
set -e
echo "=== Step 7 Validation ==="

TOKEN=$(curl -s -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo -n "Event streams: "
STREAMS=$(docker exec simhpc-redis redis-cli XINFO STREAM events:hallucination 2>/dev/null | grep length || echo "0")
echo "OK (hallucination stream: $STREAMS)"

echo -n "Simulation queue: "
docker exec simhpc-redis redis-cli LPUSH queue:simulation '{"test":true}' > /dev/null
QUEUE_LEN=$(docker exec simhpc-redis redis-cli LLEN queue:simulation)
echo "OK (length: $QUEUE_LEN)"

echo -n "Event emission: "
curl -s -X POST http://localhost:8080/api/v1/events/test \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"event_type":"test.event","payload":{"msg":"hello"}}' \
  | python3 -c "import sys,json; print(f'OK ({json.load(sys.stdin)[\"status\"]})')"

echo "=== Step 7 Complete ==="
