#!/usr/bin/env python3
"""
SimHPC Autoscaler
=================
Manages RunPod GPU fleet scaling based on queue depth.
"""

import time
import os
from pathlib import Path

from backend.runtime.queue import PersistentQueue


class Autoscaler:
    def __init__(self):
        self.min_workers = int(os.getenv("MIN_WARM_WORKERS", 1))
        self.max_workers = int(os.getenv("MAX_WORKERS", 8))
        self.queue = PersistentQueue()

    def get_queue_length(self) -> int:
        return len(self.queue.snapshot()) if hasattr(self.queue, 'snapshot') else 0

    def scale(self):
        queue_len = self.get_queue_length()
        target = max(self.min_workers, min(self.max_workers, (queue_len // 3) + 1))

        print(f"📈 Autoscaler: Queue={queue_len} | Target workers={target}")
        # In production: call RunPod API to scale pods here
        # For now: just logging
        return target


def main():
    print("🔄 SimHPC Autoscaler Started")
    scaler = Autoscaler()

    while True:
        try:
            scaler.scale()
            time.sleep(30)  # Check every 30 seconds
        except Exception as e:
            print(f"Autoscaler error: {e}")
            time.sleep(60)


if __name__ == "__main__":
    main()
