from backend.runtime.manifest import load_manifest
from backend.runtime.optimizer import DAGOptimizer
from backend.runtime.replay import ReplayEngine


class ExecutionIntelligence:
    def __init__(self):
        self.replay = ReplayEngine()
        self.optimizer = DAGOptimizer()

    def full_analysis(self):
        """Run complete intelligence suite."""
        manifest = load_manifest()

        optimized = self.optimizer.optimize(manifest)

        replay_result = None
        try:
            replay_result = self.replay.replay("latest", lambda n, i: {"status": "replayed"})
        except FileNotFoundError:
            pass

        return {
            "manifest_version": manifest["version"],
            "nodes": len(manifest["nodes"]),
            "optimized_nodes": optimized["optimized_count"],
            "replay_result": replay_result,
            "recommendation": "Run optimizer before production"
            if optimized["optimized_count"] < len(manifest["nodes"])
            else "DAG is optimal",
        }


INTELLIGENCE = ExecutionIntelligence()
