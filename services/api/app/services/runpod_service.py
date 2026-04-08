"""
RunPod Service — API Layer integration for fleet management.
Mirrors core GraphQL logic from worker/runpod_api.py for direct responsiveness.
"""

import os
import logging
import requests
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
RUNPOD_GQL_URL = f"https://api.runpod.io/graphql?api_key={RUNPOD_API_KEY}"

def _gql(query: str) -> dict:
    """Execute a RunPod GraphQL query."""
    if not RUNPOD_API_KEY:
        raise RuntimeError("RUNPOD_API_KEY not set")
    resp = requests.post(RUNPOD_GQL_URL, json={"query": query}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"RunPod GraphQL error: {data['errors']}")
    return data

def list_pods() -> List[Dict]:
    """Fetch all pods for the account."""
    query = """
    query {
      myself {
        pods {
          id
          name
          desiredStatus
          imageName
          gpuDisplayName
          costPerHr
        }
      }
    }
    """
    res = _gql(query)
    return res["data"]["myself"]["pods"]

def stop_pod(pod_id: str) -> dict:
    """Stop a pod via direct GraphQL call."""
    query = f"""
    mutation {{
      podStop(input: {{ podId: "{pod_id}" }}) {{
        id
        desiredStatus
      }}
    }}
    """
    res = _gql(query)
    logger.info(f"API: Direct Pod STOP sent for {pod_id}")
    return res["data"]["podStop"]

def terminate_pod(pod_id: str) -> dict:
    """Terminate a pod via direct GraphQL call."""
    query = f"""
    mutation {{
      podTerminate(input: {{ podId: "{pod_id}" }})
    }}
    """
    res = _gql(query)
    logger.info(f"API: Direct Pod TERMINATE sent for {pod_id}")
    return {"pod_id": pod_id, "status": "TERMINATED"}

def resume_pod(pod_id: str) -> dict:
    """Resume a stopped pod via direct GraphQL call."""
    query = f"""
    mutation {{
      podResume(input: {{ podId: "{pod_id}", gpuCount: 1 }}) {{
        id
        desiredStatus
      }}
    }}
    """
    res = _gql(query)
    logger.info(f"API: Direct Pod RESUME sent for {pod_id}")
    return res["data"]["podResume"]
