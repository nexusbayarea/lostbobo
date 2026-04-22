"""
scaler_engine loop for scaling worker pods based on queue depth
"""

import logging
import time

from backend.app.core.config import get_settings
from backend.app.core.queue import redis_client

settings = get_settings()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_queue_depth() -> int:
    """
    Get total depth across all priority queues
    """
    high_depth = redis_client.llen(settings.QUEUE_HIGH)
    med_depth = redis_client.llen(settings.QUEUE_MED)
    default_depth = redis_client.llen(settings.QUEUE_DEFAULT)

    return high_depth + med_depth + default_depth


def get_current_worker_count() -> int:
    """
    Get current number of worker pods
    In production, this would call RunPod API or Kubernetes
    For now, return a placeholder
    """
    return settings.MIN_WARM_WORKERS


def calculate_target_workers(queue_depth: int) -> int:
    """
    Calculate target number of workers based on queue depth
    """
    if queue_depth == 0:
        return settings.MIN_WARM_WORKERS
    elif queue_depth < 20:
        return 3
    elif queue_depth < 100:
        return 8
    else:
        return 20


def scale_workers(target_count: int) -> bool:
    """
    Scale worker pods to target count
    """
    current_count = get_current_worker_count()

    if target_count == current_count:
        logger.info(f"No scaling needed. Current workers: {current_count}")
        return True

    if target_count > current_count:
        to_add = target_count - current_count
        logger.info(f"Scaling up by {to_add} workers (from {current_count} to {target_count})")
        return True
    else:
        to_remove = current_count - target_count
        logger.info(f"Scaling down by {to_remove} workers (from {current_count} to {target_count})")
        return True


def scaler_engine():
    """scaler_engine loop"""
    logger.info("Starting autoscaler...")

    while True:
        try:
            queue_depth = get_queue_depth()
            logger.info(f"Current queue depth: {queue_depth}")

            target_workers = calculate_target_workers(queue_depth)
            logger.info(f"Target worker count: {target_workers}")

            scale_workers(target_workers)
            time.sleep(30)

        except Exception as e:
            logger.error(f"Error in autoscaler loop: {e}")
            time.sleep(60)


# CRITICAL FIX: In Python, this must ALWAYS be "__main__", but it calls your new function.
if __name__ == "__main__":
    scaler_engine()
