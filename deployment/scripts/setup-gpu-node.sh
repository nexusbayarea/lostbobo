#!/bin/bash
# Bootstrap script for RunPod A40 GPU node.
set -e

echo "=== SimHPC GPU Node Setup ==="

command -v docker >/dev/null 2>&1 || { echo "Docker required"; exit 1; }
command -v nvidia-smi >/dev/null 2>&1 || { echo "NVIDIA driver required"; exit 1; }

if [ ! -d "simhpc-gamma" ]; then
    git clone https://github.com/YOUR_ORG/simhpc-gamma.git
    cd simhpc-gamma
else
    cd simhpc-gamma
    git pull
fi

if [ ! -f ".env" ]; then
    cp deployment/.env.example .env
    echo "Edit .env with CPU_NODE_IP pointing to your CPU node."
    exit 0
fi

docker compose -f deployment/docker-compose-gpu.yml pull
docker compose -f deployment/docker-compose-gpu.yml up -d

echo "=== GPU Node Setup Complete ==="
