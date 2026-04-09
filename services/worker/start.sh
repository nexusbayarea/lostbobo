#!/bin/bash

echo "Starting SimHPC v2.5.6 Unified..."

# Kill Jupyter on 8888
fuser -k 8888/tcp || true

cd /app
export PYTHONPATH=/app

echo "Verifying SB Connectivity..."
infisical run -- python3 -c "import os; exit(0) if os.getenv('SB_URL') else exit(1)"

if [ $? -eq 0 ]; then
    echo "Starting FastAPI Gateway (Port 8888)..."
    # Killing jupyter on 8888 and starting YOUR api.py (Unified Orchestrator)
    fuser -k 8888/tcp || true && python3 -m uvicorn api:app --host 0.0.0.0 --port 8888 --forwarded-allow-ips='*' &
else
    echo "SB Credentials missing in Infisical. Check SB_URL and SB_ANON_KEY."
    exit 1
fi

echo "Starting Physics Worker..."
python3 -u worker.py &

echo "Starting Autoscaler..."
python3 -u autoscaler.py &

wait