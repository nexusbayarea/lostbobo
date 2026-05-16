#!/bin/bash
set -e
echo "=== Step 6 Validation ==="

TOKEN=$(curl -s -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

echo -n "Module runtime: "
python3 -c "import grpc; ch = grpc.insecure_channel('localhost:50052'); grpc.channel_ready_future(ch).result(timeout=5)" && echo "OK" || echo "FAIL"

echo -n "Plugins loaded: "
curl -s http://localhost:8080/api/v1/plugins \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "import sys,json; plugins=json.load(sys.stdin)['plugins']; print(f'OK ({len(plugins)} plugins: {plugins})')"

echo -n "EV module: "
curl -s -X POST http://localhost:8080/api/v1/simulate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"capability":"ev.thermal","payload":{"battery_temp":25},"tenant_id":"test"}' \
  | python3 -c "import sys,json; print(f'OK (job_id={json.load(sys.stdin)[\"job_id\"]})')"

echo "=== Step 6 Complete ==="
