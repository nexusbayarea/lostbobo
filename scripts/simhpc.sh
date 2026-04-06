#!/bin/bash
# SimHPC CLI Skill
case $1 in
  deploy)
    python3 /workspace/scripts/deploy_to_runpod.py
    ;;
  logs)
    # Quick skill to see your API logs
    tail -f /runpod-volume/app/api_logs.txt
    ;;
  restart-api)
    # Quick skill to bounce the FastAPI server
    kill -9 $(lsof -t -i:8000)
    /runpod-volume/start.sh
    ;;
  *)
    echo "Usage: simhpc {deploy|logs|restart-api}"
    ;;
esac
