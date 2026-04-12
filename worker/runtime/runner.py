"""
Main execution loop for worker service
"""

import time
import uuid
import signal
import sys
from typing import Optional
from app.services.worker.runtime.bootstrap import preload_engine, preload_runtime
from app.services.worker.runtime.state import (
    claim_job,
    renew_lease,
    update_job_status,
    increment_attempt_count,
)
from app.services.worker.runtime.execute import execute_job
from app.core.config import settings

# Global flag for graceful shutdown
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_requested
    print("\nShutdown signal received. Finishing current job...")
    shutdown_requested = True


def main():
    """Main worker execution loop"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Generate unique worker ID
    worker_id = f"worker-{uuid.uuid4()}"
    print(f"Starting worker {worker_id}")

    # Preload engine and runtime components
    print("Preloading components...")
    preload_engine()
    preload_runtime()
    print("Components preloaded. Starting job processing loop...")

    # Main processing loop
    while not shutdown_requested:
        try:
            # Claim a job from the queue
            job_data = claim_job(worker_id)

            if job_data is None:
                # No jobs available, sleep briefly before trying again
                time.sleep(1)
                continue

            job_id = job_data["id"]
            lease_id = job_data.get("lease_id")

            print(f"Claimed job {job_id}")

            # Execute the job
            result = execute_job(job_data)

            # Update job status based on execution result
            if result["success"]:
                print(f"Job {job_id} completed successfully")
                # Attempt count is already incremented in execute_job via update_job_status
            else:
                print(f"Job {job_id} failed: {result.get('error', 'Unknown error')}")
                # Increment attempt count for failed jobs
                increment_attempt_count(job_id)

                # Check if we should retry based on attempt count
                # Get current job status to check attempt count
                from app.services.worker.runtime.state import get_job

                current_job = get_job(job_id)
                if current_job and current_job.get("attempt_count", 0) < 3:
                    # Re-queue for retry (status will be updated by increment_attempt_count)
                    print(
                        f"Job {job_id} will be retried (attempt {current_job.get('attempt_count', 0)})"
                    )
                else:
                    print(
                        f"Job {job_id} exceeded max attempts, marking as failed permanently"
                    )

            # Small delay between jobs to prevent tight loop
            time.sleep(0.1)

        except Exception as e:
            print(f"Error in worker loop: {e}")
            time.sleep(5)  # Longer sleep on unexpected errors

    print(f"Worker {worker_id} shutting down gracefully...")


if __name__ == "__main__":
    main()
