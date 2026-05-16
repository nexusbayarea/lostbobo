#!/bin/bash
# Run ONCE after first docker compose up on RunPod.
# This caches models into the persistent volume so they survive container restarts.

echo "Pulling models into Ollama container..."

docker exec simhpc-ollama ollama pull nomic-embed-text:v2-moe
docker exec simhpc-ollama ollama pull gemma:2b
docker exec simhpc-ollama ollama pull qwen2.5:3b-instruct
docker exec simhpc-ollama ollama pull numarkdown:8b-thinking

echo "Verifying models..."
docker exec simhpc-ollama ollama list

echo "Done. Models cached in persistent volume."
