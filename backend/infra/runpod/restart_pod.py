#!/usr/bin/env python3
"""
Update/Restart RunPod Pod
"""

import os
import time

import runpod

API_KEY = os.getenv("RUNPOD_API_KEY")
if not API_KEY:
    raise ValueError("RUNPOD_API_KEY not set")

runpod.api_key = API_KEY

POD_ID = os.getenv("RUNPOD_POD_ID", "q41n3g4zwr84wt")

print(f"Stopping pod {POD_ID}...")
runpod.stop_pod(POD_ID)

print("Waiting for pod to stop...")
time.sleep(5)

print(f"Starting pod {POD_ID}...")
