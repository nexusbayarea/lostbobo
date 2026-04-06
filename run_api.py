import uvicorn
import os
import sys

# Ensure the root and services/api are in the path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "services", "api"))

if __name__ == "__main__":
    print("Starting FastAPI server on 0.0.0.0:8000...")
    # We point to services.api.api:app as that is the verified main entry point
    uvicorn.run("services.api.api:app", host="0.0.0.0", port=8000, reload=True)
