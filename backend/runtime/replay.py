from collections.abc import Callable
from pathlib import Path

from backend.runtime.trace import ExecutionTrace


class ReplayEngine:
    def __init__(self):
        self.traces_dir = Path("trace_history")
        self.traces_dir.mkdir(exist_ok=True)

    def save_trace(self, trace: ExecutionTrace, name: str = "latest"):
        path = self.traces_dir / f"{name}.json"
        trace.save(str(path))
        print(f"Trace saved: {path}")

    def load_trace(self, name: str = "latest") -> ExecutionTrace:
        path = self.traces_dir / f"{name}.json"
        if not path.exists():
            raise FileNotFoundError(f"Trace {name} not found")
        return ExecutionTrace.load(str(path))

    def replay(self, trace_name: str, executor: Callable) -> dict:
        """Replay a saved trace and compare results."""
        original = self.load_trace(trace_name)
        print(f"Replaying trace: {trace_name} ({len(original.nodes)} nodes)")

        results = []
        for node in original.nodes:
            try:
                actual = executor(node.name, node.input)
                match = actual == node.output
                results.append(
                    {
                        "node": node.name,
                        "status": "match" if match else "diff",
                        "expected": node.output,
                        "actual": actual,
                    }
                )
            except Exception as e:
                results.append({"node": node.name, "status": "error", "error": str(e)})

        return {"trace": trace_name, "results": results, "perfect_replay": all(r["status"] == "match" for r in results)}
