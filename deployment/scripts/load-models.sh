#!/bin/bash
set -e
echo "=== Loading Local Models ==="

docker exec simhpc-ollama ollama pull gemma:2b
docker exec simhpc-ollama ollama pull qwen2.5:3b-instruct

echo "Installed models:"
docker exec simhpc-ollama ollama list

echo -n "Gemma 2B test: "
curl -s http://localhost:11434/api/generate -d '{"model":"gemma:2b","prompt":"Say hello","stream":false}' | python3 -c "import sys,json; print(json.load(sys.stdin)['response'][:50])"

echo -n "Qwen 3B test: "
curl -s http://localhost:11434/api/generate -d '{"model":"qwen2.5:3b-instruct","prompt":"What is 2+2?","stream":false}' | python3 -c "import sys,json; print(json.load(sys.stdin)['response'][:50])"

echo "=== Step 2 Complete ==="
