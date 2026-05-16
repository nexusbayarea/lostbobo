#!/bin/bash
# Bootstrap script for RunPod CPU node.
set -e

echo "=== SimHPC CPU Node Setup ==="

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Docker required"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "Git required"; exit 1; }

# Clone if not already present
if [ ! -d "simhpc-gamma" ]; then
    git clone https://github.com/YOUR_ORG/simhpc-gamma.git
    cd simhpc-gamma
else
    cd simhpc-gamma
    git pull
fi

# Create .env from example if not exists
if [ ! -f ".env" ]; then
    cp deployment/.env.example .env
    echo "Edit .env with your configuration, then run:"
    echo "  docker compose -f deployment/docker-compose-cpu.yml up -d"
    exit 0
fi

# Pull images and start
docker compose -f deployment/docker-compose-cpu.yml pull
docker compose -f deployment/docker-compose-cpu.yml up -d

echo "Waiting for services..."
sleep 15

# Run health check
bash deployment/scripts/health-check.sh

echo "=== Setup Complete ==="
echo "Run 'bash deployment/scripts/pull-models.sh' to cache Ollama models."
