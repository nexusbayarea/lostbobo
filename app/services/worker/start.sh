#!/bin/bash
set -e

echo "🚀 [SimHPC] Starting API directly (debug mode) - $(date)"

# Clear port
fuser -k 8080/tcp || true

echo "Starting uvicorn on 0.0.0.0:8080..."

# Start API directly - this is the most reliable way to see errors
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --log-level info