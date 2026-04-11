"""
SimHPC Production Autoscaler (v2.7.5)
Queue-aware elastic scaling for RunPod GPU workers.
"""

import os
import time
import json
import logging
import threading
import requests
from datetime import datetime
from redis import Redis

# --- CONFIG ---
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUE_NAME = os.getenv("QUEUE_NAME", "simhpc_jobs")
EVENTS_CHANNEL = "jobs:events"
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "10"))

# RunPod Config
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
POD_TEMPLATE_ID = os.getenv("RUNPOD_TEMPLATE_ID")
MIN_WORKERS = int(os.getenv("MIN_WORKERS", "1"))
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "10"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [AUTOSCALER] %(levelname)s - %(message)s",
)
logger = logging.getLogger("autoscaler")

redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

# --- METRICS ---

def get_queue_depth():
    """Get number of pending jobs in Redis."""
    return redis_client.llen(QUEUE_NAME)

def get_active_workers():
    """Get count of workers currently reporting heartbeats."""
    workers = redis_client.hgetall("sim:workers")
    now = time.time()
    active_count = 0
    for worker_id, last_seen in workers.items():
        if now - float(last_seen) < 30:  # Active within 30s
            active_count += 1
    return active_count

def get_oldest_job_age():
    """Estimate age of the oldest job in the queue (seconds)."""
    # Peek at the tail of the list (oldest job is usually at the end if we use lpush/rpop)
    # Our system uses lpush (API) and brpop (Worker), so oldest is at the end (index -1)
    job_raw = redis_client.lindex(QUEUE_NAME, -1)
    if not job_raw:
        return 0
    try:
        job_data = json.loads(job_raw)
        created_at = job_data.get("created_at", time.time())
        return max(0, time.time() - float(created_at))
    except Exception:
        return 0

# --- SCALING ACTIONS ---

def spawn_worker():
    """Trigger RunPod API to create a new GPU pod."""
    if not RUNPOD_API_KEY or not POD_TEMPLATE_ID:
        logger.error("Missing RUNPOD_API_KEY or RUNPOD_TEMPLATE_ID")
        return False

    logger.info("🚀 Spawning new RunPod worker...")
    url = "https://api.runpod.io/v2/pods"
    payload = {
        "templateId": POD_TEMPLATE_ID,
        "name": f"sim-worker-{int(time.time())}",
        "cloudType": "SECURE",
        "gpuCount": 1
    }
    headers = {"Authorization": f"Bearer {RUNPOD_API_KEY}"}

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code == 200:
            logger.info(f"✅ Spawned pod: {resp.json().get('id')}")
            return True
        else:
            logger.error(f"❌ RunPod spawn failed: {resp.text}")
            return False
    except Exception as e:
        logger.error(f"Spawn exception: {e}")
        return False

def cleanup_stale_workers():
    """Remove workers from the registry that haven't heartbeated in > 60s."""
    workers = redis_client.hgetall("sim:workers")
    now = time.time()
    for worker_id, last_seen in workers.items():
        if now - float(last_seen) > 60:
            logger.info(f"🧹 Removing stale worker: {worker_id}")
            redis_client.hdel("sim:workers", worker_id)
            redis_client.srem("workers:active", worker_id)

# --- CORE LOGIC ---

def scale_logic():
    """Calculate desired workers based on queue pressure and act."""
    queue_depth = get_queue_depth()
    active_workers = get_active_workers()
    oldest_age = get_oldest_job_age()

    # Pressure Function: queue depth + age factor
    # Every 10s of age counts as 1 "virtual" pending job
    pressure = queue_depth + (oldest_age / 10.0)
    
    # Desired: sqrt of pressure (smooth scaling) capped by limits
    # e.g., 4 jobs -> 2 workers, 16 jobs -> 4 workers, 100 jobs -> 10 workers
    desired = min(MAX_WORKERS, max(MIN_WORKERS, int(pressure ** 0.5)))

    logger.info(f"Stats: queue={queue_depth} active={active_workers} age={oldest_age:.1f}s | Pressure={pressure:.1f} Desired={desired}")

    if active_workers < desired:
        # Scale up
        diff = desired - active_workers
        logger.info(f"📈 Scaling up: +{diff} workers")
        for _ in range(diff):
            spawn_worker()
            time.sleep(1) # Small stagger
    
    # Note: Scaling down is handled by workers self-terminating on idle (RunPod standard)
    # or by this autoscaler sending stop commands (implemented in future iteration).

def log_status():
    """Log current system status for observability."""
    status = {
        "queue_depth": get_queue_depth(),
        "active_workers": get_active_workers(),
        "timestamp": datetime.utcnow().isoformat(),
    }
    redis_client.set("autoscaler:status", json.dumps(status))

def system_ready():
    """Check if the system (Redis) is reachable."""
    try:
        return redis_client.ping()
    except Exception:
        return False

def main():
    logger.info("=" * 60)
    logger.info("SimHPC Autoscaler v2.7.5 — Production Queue-Aware")
    logger.info(f"Target: {MIN_WORKERS}-{MAX_WORKERS} workers")
    logger.info("=" * 60)

    while True:
        try:
            if not system_ready():
                logger.warning("⛔ system (Redis) not ready, skipping loop")
                time.sleep(5)
                continue

            cleanup_stale_workers()
            scale_logic()
            log_status()
            
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Shutdown requested")
            break
        except Exception as e:
            logger.error(f"Autoscaler error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
