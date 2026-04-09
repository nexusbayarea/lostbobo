#!/bin/bash
set -e

echo "[1/2] Syncing to GitHub..."
git add .
git commit -m "ci: deploy SimHPC v2.6.4"
git push origin main

echo "[2/2] Deployment triggered"
echo "=== Done ==="