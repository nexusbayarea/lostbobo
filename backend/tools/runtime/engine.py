from backend.tools.runtime.backends.registry import BACKENDS
from backend.tools.runtime.contract import compute_contract
from backend.tools.runtime.trace import record, load
from backend.tools.runtime.diff import should_execute

class ExecutionEngine:
    def run_node(self, node, context):
        node_id = node["id"]

        contract = compute_contract(node)

        previous = load(node_id, context["workspace"])

        if not should_execute(node, previous, contract):
            # Mark result as cached/reused if needed
            return previous["result"]

        backend = BACKENDS[node["type"]]
        result = backend.execute(node, context)
        # Mark as newly executed
        result["executed"] = True

        record(node_id, contract, result, context["workspace"])

        return result

def run_dag(nodes, context):
    engine = ExecutionEngine()
    results = {}
    dirty = set()

    for node in nodes:
        # Check downstream invalidation
        deps = node.get("deps", [])
        if any(d in dirty for d in deps):
            dirty.add(node["id"])

        result = engine.run_node(node, context)
        results[node["id"]] = result

        # mark dirty if this node was actually executed
        if result.get("executed"):
            dirty.add(node["id"])

    return results
