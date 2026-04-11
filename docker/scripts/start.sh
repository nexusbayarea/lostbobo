#!/bin/bash
set -e

echo "🚀 [SimHPC] Starting API directly on port 8080 - $(date)"

# Clear port in case of stale process using lsof if available
if command -v lsof >/dev/null 2>&1; then
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
elif command -v fuser >/dev/null 2>&1; then
    fuser -k 8080/tcp || true
else
    # Fallback: try to kill any process using port 8080
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
fi

echo "Starting uvicorn..."
exec python3 -m uvicorn main:app \
    --host 0.0.0.0 \
    --port 8080 \
    --log-level info \
    --workers 2
