#!/bin/bash
# Run ONCE on RunPod to pre-cache models into the persistent volume.
# This is NOT in the Dockerfile because models are too large for Git/GitHub.

ollama serve &
OLLAMA_PID=$!
sleep 5

echo "Pulling embedding model..."
ollama pull nomic-embed-text:v2-moe

echo "Pulling lightweight models..."
ollama pull gemma:2b
ollama pull qwen2.5:3b-instruct

echo "Pulling ingestion model..."
ollama pull numarkdown:8b-thinking

echo "Verifying models..."
ollama list

kill $OLLAMA_PID
echo "Done. Models cached in /root/.ollama"
