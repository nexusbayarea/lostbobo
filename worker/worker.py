"""
Worker Process — Pulls tasks from Redis queue, executes, stores results

Run multiple instances for horizontal scaling:
    python -m worker.worker
    python -m worker.worker
    python -m worker.worker
"""

import time
from pathlib import Path
import sys

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from app.runtime.queue import TaskQueue
from app.runtime.state import ResultStore
from app.runtime.dispatch import dispatch
from app.runtime.dag import DAG
from worker.tasks import task_a, task_b, task_multiply, task_sum


DAG_BUILDERS = {
    "test": lambda: DAG().add("task_a", task_a).add("task_b", task_b, deps=["task_a"]),
}


def worker_loop(
    dag: DAG, context: dict = None, queue_url: str = "redis://localhost:6379/0"
) -> None:
    context = context or {}
    queue = TaskQueue(url=queue_url)
    store = ResultStore(url=queue_url)

    print(f"[WORKER] Started, watching queue...")

    while True:
        task = queue.pop()

        if not task:
            time.sleep(0.1)
            continue

        name = task["name"]
        node = dag.get(name)

        if not node:
            print(f"[WORKER] Unknown task: {name}")
            continue

        ready = all(store.exists(dep) for dep in node.deps)
        if not ready:
            queue.push(task)
            time.sleep(0.05)
            continue

        print(f"[WORKER] Executing: {name}")

        inputs = {dep: store.get(dep) for dep in node.deps}

        result = dispatch(node, inputs, context)

        if not store.exists(name):
            store.set(name, result)
            print(f"[WORKER] Completed: {name}")

            for n, other in dag.nodes.items():
                if name in other.deps:
                    if all(store.exists(d) for d in other.deps):
                        queue.push({"name": n})


def main():
    dag_name = sys.argv[1] if len(sys.argv) > 1 else "test"
    queue_url = sys.argv[2] if len(sys.argv) > 2 else "redis://localhost:6379/0"

    builder = DAG_BUILDERS.get(dag_name)
    if not builder:
        print(f"Unknown DAG: {dag_name}")
        sys.exit(1)

    dag = builder()
    dag.validate()

    worker_loop(dag, context={"mode": "local"}, queue_url=queue_url)


if __name__ == "__main__":
    main()
