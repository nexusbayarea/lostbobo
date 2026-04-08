#!/bin/bash

set -e

echo "[1/5] Running Local Build Test..."
npm run build

if [ $? -ne 0 ]; then
    echo "Local build failed. Fix pathing/imports before pushing."
    exit 1
fi

echo "[2/5] Build passed. Syncing to GitHub..."
git add . 
git commit -m "ci: trigger docker build and deploy to RunPod"
git push origin main

echo "[3/5] Waiting for Docker build to complete..."
sleep 30

echo "[4/5] Deploying to RunPod..."
# RunPod deployment happens via GitHub Actions workflow
gh workflow run auto-deploy-runpod.yml

echo "[5/5] Deployment triggered."
echo "=== Deployment Complete ==="
echo "- Vercel: https://simhpc.com"
echo "- Docker: simhpcworker/simhpc-unified:latest"
echo "- RunPod: Auto-deploy workflow triggered"