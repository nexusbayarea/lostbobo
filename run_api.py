import uvicorn
import os
import sys

# 1. Point specifically to the directory containing worker.py
# On your pod, this is /runpod-volume/app
app_path = "/runpod-volume/app"

# Fallback for local development if /runpod-volume/app doesn't exist
if not os.path.exists(app_path):
    app_path = os.path.join(os.getcwd(), "services", "api")
    entry_point = "api:app"
else:
    entry_point = "worker:app"

sys.path.append(app_path)
os.chdir(app_path)

if __name__ == "__main__":
    print(f"Starting FastAPI server from {app_path}...")
    # 2. Change 'services.api.api:app' to 'worker:app' 
    # This matches the worker.py file found in your app folder
    uvicorn.run(entry_point, host="0.0.0.0", port=8000, reload=True)
