"""
Task Queue — Thread-safe in-memory queue for distributed-ready execution

Provides backpressure and decoupled execution foundation.
"""

from queue import Queue, Empty
from typing import Any, Optional


class TaskQueue:
    def __init__(self):
        self.q = Queue()

    def push(self, task: Any) -> None:
        self.q.put(task)

    def pop(self) -> Optional[Any]:
        try:
            return self.q.get(timeout=0.1)
        except Empty:
            return None

    def task_done(self) -> None:
        self.q.task_done()

    def join(self) -> None:
        self.q.join()

    def empty(self) -> bool:
        return self.q.empty()

    def __len__(self) -> int:
        return self.q.qsize()
