from backend.runtime.ci_graph import CI_GRAPH, CINode
from backend.runtime.graph import GRAPH, Node


def register_ci_nodes():
    GRAPH.register(Node(id="lint", deps=[], fn=lambda: print("lint")))
    GRAPH.register(Node(id="lockfile", deps=["lint"], fn=lambda: print("lockfile")))
    GRAPH.register(Node(id="pruning", deps=["lint"], fn=lambda: print("pruning")))
    GRAPH.register(Node(id="boundaries", deps=["lockfile"], fn=lambda: print("boundaries")))
    GRAPH.register(Node(id="api", deps=["boundaries", "pruning"], fn=lambda: print("api")))


def register_ci_graph_nodes():
    CI_GRAPH.add(CINode(id="lint", deps=[], fn=lambda: 0))
    CI_GRAPH.add(CINode(id="lockfile", deps=["lint"], fn=lambda: 0))
    CI_GRAPH.add(CINode(id="pruning", deps=["lint"], fn=lambda: 0))
    CI_GRAPH.add(CINode(id="boundaries", deps=["lockfile"], fn=lambda: 0))
    CI_GRAPH.add(CINode(id="api", deps=["boundaries", "pruning"], fn=lambda: 0))


register_ci_nodes()
register_ci_graph_nodes()
