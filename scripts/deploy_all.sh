#!/bin/bash
set -e

echo "[1/3] Building & pushing Docker image..."
docker build -f docker/images/Dockerfile.unified -t simhpcworker/simhpc-unified:latest .
docker push simhpcworker/simhpc-unified:latest

echo "[2/3] Restarting RunPod pod..."
python infra/runpod/restart_pod.py

echo "[3/3] Deployment complete"
echo "=== Done ==="
