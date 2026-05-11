"""
Serialisation of DAG IR to/from JSON and binary formats.
"""

from __future__ import annotations

from pathlib import Path

from backend.core.dag.models import DAGGraph


def dumps(graph: DAGGraph, indent: int = 2) -> str:
    """Serialize DAGGraph to JSON string."""
    return graph.model_dump_json(indent=indent)


def loads(json_str: str) -> DAGGraph:
    """Deserialize JSON string back to DAGGraph."""
    return DAGGraph.model_validate_json(json_str)


def save(graph: DAGGraph, path: Path) -> None:
    """Write DAGGraph to a file."""
    path.write_text(dumps(graph))


def load(path: Path) -> DAGGraph:
    """Read DAGGraph from a file."""
    return loads(path.read_text())
