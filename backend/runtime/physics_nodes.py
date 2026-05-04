from backend.runtime.graph import GRAPH, Node
from backend.runtime.kernel import execute_node as kernel_execute


def run_mfem_solve(node: dict) -> dict:
    """Real MFEM solver node."""
    print(f"Running MFEM solve: {node.get('mesh')} with {node.get('params', {})}")
    result = kernel_execute(node)
    return {"status": "completed", "solver": "mfem", "result": result}


def register_physics_nodes():
    """Register physics-heavy DAG nodes."""

    GRAPH.register(Node(id="mfem.solve", deps=[], fn=run_mfem_solve, metadata={"gpu": True, "timeout": 300}))

    GRAPH.register(
        Node(
            id="sundials.integrate",
            deps=["mfem.solve"],
            fn=lambda node: {"status": "integrated", "solver": "sundials"},
            metadata={"gpu": False},
        )
    )

    print("Physics nodes registered")


register_physics_nodes()
