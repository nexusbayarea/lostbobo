from backend.runtime.graph import GRAPH, Node
from backend.runtime.kernel import KERNEL


def register_all_nodes():
    """Register all known nodes in the execution graph."""

    import tools.ci_steps.api as api
    import tools.ci_steps.boundaries as boundaries
    import tools.ci_steps.lint as lint
    import tools.ci_steps.lockfile as lockfile
    import tools.ci_steps.pruning as pruning

    GRAPH.register(Node(id="lint", deps=[], fn=lint.run))
    GRAPH.register(Node(id="lockfile", deps=["lint"], fn=lockfile.run))
    GRAPH.register(Node(id="pruning", deps=["lockfile"], fn=pruning.run))
    GRAPH.register(Node(id="boundaries", deps=["pruning"], fn=boundaries.run))
    GRAPH.register(Node(id="api_purity", deps=["boundaries"], fn=api.run))

    GRAPH.register(Node(id="kernel_boot", deps=["api_purity"], fn=KERNEL.boot))

    print(f"Registered {len(GRAPH.nodes)} nodes in ExecutionGraph")


register_all_nodes()
