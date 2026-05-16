#!/bin/bash
# =============================================================================
# SimHPC VPS Update — pull latest images and restart
# Used by CI/CD deploy step. Also safe for manual use.
# =============================================================================
set -euo pipefail

echo "=== SimHPC VPS Update ==="

cd /mnt/simhpc_vps/simhpc-gamma

echo "Pulling latest code..."
git pull origin main

echo "Pulling latest Docker images..."
docker compose -f deployment/docker-compose.yml pull

echo "Recreating containers..."
docker compose -f deployment/docker-compose.yml up -d --remove-orphans

echo "Waiting for services..."
sleep 10

echo "Validating..."
bash deployment/scripts/validate-cpu.sh

echo "=== Update Complete ==="
