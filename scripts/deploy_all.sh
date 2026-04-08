#!/bin/bash

set -e

echo "[1/4] Syncing Infisical to GitHub..."
git add . 
git commit -m "ci: trigger docker build and deploy to RunPod"
git push origin main

echo "[2/4] Waiting for Docker build..."
sleep 30

echo "[3/4] Deploying to RunPod..."
gh workflow run auto-deploy-runpod.yml

echo "[4/4] Deployment triggered."
echo "=== Deployment Complete ==="