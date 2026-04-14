"""
Scheduler — Topological execution order + queue-driven execution + multi-worker support

Provides:
- topological_sort: deterministic ordering
- Scheduler: queue-driven execution with backpressure and parallelism
"""

import threading
from typing import Any, Dict

from app.runtime.queue import TaskQueue


def topological_sort(nodes: Dict[str, "Node"]) -> list:
    visited = set()
    order = []

    def dfs(name: str) -> None:
        if name in visited:
            return
        visited.add(name)

        node = nodes[name]
        for dep in node.deps:
            dfs(dep)

        order.append(name)

    for name in nodes:
        dfs(name)

    return order


class Scheduler:
    def __init__(self, dag):
        self.dag = dag
        self.queue = TaskQueue()
        self.results = {}
        self.lock = threading.Lock()
        self.active_workers = 0

    def seed(self) -> None:
        for name, node in self.dag.nodes.items():
            if not node.deps:
                self.queue.push(name)

    def ready(self, node_name: str) -> bool:
        node = self.dag.nodes[node_name]
        return all(dep in self.results for dep in node.deps)

    def worker(self, dispatch: Any, context: Dict[str, Any]) -> None:
        while True:
            name = self.queue.pop()
            if name is None:
                return

            node = self.dag.nodes[name]

            with self.lock:
                if not self.ready(name):
                    self.queue.push(name)
                    self.queue.task_done()
                    continue

                inputs = {dep: self.results[dep] for dep in node.deps}

            result = dispatch(node, inputs, context)

            with self.lock:
                if name in self.results:
                    self.queue.task_done()
                    continue

                self.results[name] = result

                for n, other in self.dag.nodes.items():
                    if name in other.deps:
                        self.queue.push(n)

            self.queue.task_done()

    def run(
        self, dispatch: Any, context: Dict[str, Any] = None, workers: int = 1
    ) -> Dict[str, Any]:
        context = context or {}
        self.seed()

        threads = []
        for _ in range(workers):
            t = threading.Thread(target=self.worker, args=(dispatch, context))
            t.start()
            threads.append(t)

        self.queue.join()

        for t in threads:
            t.join()

        return self.results
