from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class IsolationTier(str, Enum):
    PROCESS = "process"
    WASM = "wasm"
    KATA = "kata"


class PluginPermission(str, Enum):
    GPU_ALLOCATE = "gpu.allocate"
    MEMORY_READ = "memory.read"
    MEMORY_WRITE = "memory.write"
    DAG_EXECUTE = "dag.execute"
    NETWORK_EGRESS = "network.egress"


class PluginManifest(BaseModel):
    name: str
    version: str

    capabilities: list[str]

    dag_nodes: list[str]

    permissions: list[PluginPermission]

    isolation: IsolationTier = IsolationTier.PROCESS
