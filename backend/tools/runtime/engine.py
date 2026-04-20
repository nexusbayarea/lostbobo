from backend.tools.runtime.backends.registry import BACKENDS
from backend.tools.runtime.backends.registry import BACKENDS
from backend.tools.runtime.trace import record, load
from backend.tools.runtime.planner import plan_execution

class ExecutionEngine:
    def run_node(self, node, context):
        node_id = node["id"]
        # Execution is now driven by the planner, but we record execution
        # to ensure tracing works correctly.
        backend = BACKENDS[node["type"]]
        result = backend.execute(node, context)
        result["executed"] = True
        return result

def run_dag(nodes, context):
    plan = plan_execution(nodes, context["workspace"])
    engine = ExecutionEngine()
    results = {}

    for nid in plan["ordered"]:
        node = next(n for n in nodes if n["id"] == nid)

        if nid not in plan["dirty"]:
            prev = load(nid, context["workspace"])
            results[nid] = prev["result"]
            continue

        result = engine.run_node(node, context)
        record(nid, plan["contracts"][nid], result, context["workspace"])
        results[nid] = result

    return results

