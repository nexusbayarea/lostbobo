from pathlib import Path
import json
from collections import defaultdict


class ReplayEngine:
    def __init__(self, log_path: str = "runtime_trace.json"):
        self.log_path = Path(log_path)
        self.events = self._load()

    def _load(self):
        if not self.log_path.exists():
            raise RuntimeError("No execution log found")

        return json.loads(self.log_path.read_text())

    def group_by_task(self):
        grouped = defaultdict(list)

        for e in self.events:
            grouped[e["task_id"]].append(e)

        return grouped

    def rebuild_state_timeline(self):
        """
        Reconstruct state transitions per task.
        """
        grouped = self.group_by_task()

        timeline = {}

        for task_id, events in grouped.items():
            state = "unknown"
            trace = []

            for e in sorted(events, key=lambda x: x["ts"]):
                event_type = e["type"]

                if event_type == "task_registered":
                    state = "pending"

                elif event_type == "queued":
                    state = "queued"

                elif event_type == "leased":
                    state = "leased"

                elif event_type == "success":
                    state = "success"

                elif event_type == "failure":
                    state = "failed"

                elif event_type == "retry":
                    state = "pending"

                elif event_type == "dead":
                    state = "failed"

                elif event_type == "lease_expired_requeue":
                    state = "pending"

                trace.append({
                    "ts": e["ts"],
                    "event": event_type,
                    "state": state,
                    "payload": e.get("payload"),
                })

            timeline[task_id] = trace

        return timeline

    def verify_determinism(self):
        """
        Checks whether execution had non-deterministic anomalies.
        """
        grouped = self.group_by_task()

        anomalies = []

        for task_id, events in grouped.items():
            event_types = [e["type"] for e in events]

            # Rule 1: success must not be followed by retry/requeue
            if "success" in event_types:
                success_index = next(i for i, e in enumerate(events) if e["type"] == "success")
                later_events = event_types[success_index:]

                if any(x in later_events for x in ["retry", "queued", "lease_expired_requeue"]):
                    anomalies.append((task_id, "post-success mutation"))

            # Rule 2: multiple success events
            if event_types.count("success") > 1:
                anomalies.append((task_id, "multiple success events"))

        return anomalies
