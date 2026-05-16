#!/bin/bash
set -e
echo "=== Step 3 Validation ==="

echo -n "Embedding: "
curl -s http://localhost:11434/api/embed -d '{"model":"nomic-embed-text:v2-moe","input":"test"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'OK (dim={len(d[\"embeddings\"][0])})')"

echo -n "Retrieval: "
curl -s -X POST http://localhost:8080/api/v1/rag/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query":"test query","top_k":3}' \
  | python3 -c "import sys,json; print(f'OK (docs={len(json.load(sys.stdin)[\"documents\"])})')"

echo -n "GraphRAG: "
curl -s -X POST http://localhost:8080/api/v1/rag/graph-query \
  -H "Content-Type: application/json" \
  -d '{"query_type":"traverse","start_node":"test","max_depth":1}' \
  | python3 -c "import sys,json; print(f'OK (paths={len(json.load(sys.stdin)[\"paths\"])})')"

echo "=== Step 3 Complete ==="
