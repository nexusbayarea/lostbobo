from __future__ import annotations
from enum import Enum
from typing import Dict, Optional, Any, List
from pydantic import BaseModel, Field, field_validator
from packaging.version import Version


class IsolationTier(str, Enum):
    PROCESS = "process"
    THREAD = "thread"
    CONTAINER = "container"
    WASM = "wasm"
    KATA = "kata"


class GPUProfile(str, Enum):
    NONE = "none"
    SHARED_SMALL = "shared-small"
    SHARED_MEDIUM = "shared-medium"
    SHARED_LARGE = "shared-large"
    DEDICATED_SINGLE = "dedicated-single"
    DEDICATED_MULTI = "dedicated-multi"
    MIG_QUARTER = "mig-quarter"
    MIG_HALF = "mig-half"
    MIG_FULL = "mig-full"


class ResourceQuota(BaseModel):
    cpu_cores: float = Field(default=1.0, ge=0.1, le=64.0)
    memory_mb: int = Field(default=512, ge=64, le=1048576)
    gpu_profile: GPUProfile = Field(default=GPUProfile.NONE)
    gpu_memory_mb: Optional[int] = Field(default=None, ge=128)
    storage_mb: int = Field(default=1024, ge=0)
    max_concurrent_executions: int = Field(default=10, ge=1)
    execution_timeout_seconds: int = Field(default=3600, ge=1)


class PluginPermission(str, Enum):
    DAG_EXECUTE = "dag.execute"
    MEMORY_READ = "memory.read"
    MEMORY_WRITE = "memory.write"
    GPU_ALLOCATE = "gpu.allocate"
    NETWORK_EGRESS = "network.egress"
    STORAGE_READ = "storage.read"
    STORAGE_WRITE = "storage.write"
    KERNEL_EVENTS = "kernel.events"
    LINEAGE_WRITE = "lineage.write"


class PluginPassport(BaseModel):
    plugin_id: str
    publisher: str
    version: str
    public_key: str
    permissions: list[str]
    signature: str
    trust_anchor: str | None = None


class SyscallPermission(BaseModel):
    name: str
    args_constraints: Optional[Dict[str, Any]] = None


class NetworkEgressRule(BaseModel):
    host: str
    port: int = 443
    protocol: str = "https"


class SecretScope(BaseModel):
    secret_path: str
    readonly: bool = True


class PluginPermissions(BaseModel):
    syscalls: List[SyscallPermission] = Field(default_factory=list)
    network_egress: List[NetworkEgressRule] = Field(default_factory=list)
    secrets: List[SecretScope] = Field(default_factory=list)
    capabilities_delegate: List[str] = Field(default_factory=list)


class DAGNodeDeclaration(BaseModel):
    node_type: str
    version: str = "1.0.0"
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    deterministic: bool = True
    idempotent: bool = True
    max_retries: int = 0
    timeout_seconds: int = 300
    required_capabilities: List[str] = Field(default_factory=list)


class EventSubscription(BaseModel):
    event_type: str
    filter_expression: Optional[str] = None
    priority: int = 0


class EventEmission(BaseModel):
    event_type: str
    schema_version: str = "1.0.0"
    payload_schema: Dict[str, Any] = Field(default_factory=dict)


class MemoryAccessContract(BaseModel):
    tiers: List[str] = Field(default_factory=list)
    namespaces: List[str] = Field(default_factory=list)
    read_only: bool = False
    ttl_seconds: Optional[int] = None
    confidence_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class LineageContract(BaseModel):
    record_inputs: bool = True
    record_outputs: bool = True
    record_intermediate_states: bool = False
    attestation_required: bool = False
    replay_supported: bool = False


class PluginManifest(BaseModel):
    name: str
    version: str
    description: str = ""

    author: str = ""
    author_email: str = ""
    signature: Optional[str] = None
    public_key_fingerprint: Optional[str] = None

    sdk_version_min: str = "1.0.0"
    sdk_version_max: Optional[str] = None

    capabilities: List[str] = Field(default_factory=list)
    dag_nodes: List[DAGNodeDeclaration] = Field(default_factory=list)

    isolation_tier: IsolationTier = IsolationTier.PROCESS
    resource_quota: ResourceQuota = Field(default_factory=ResourceQuota)
    permissions: PluginPermissions = Field(default_factory=PluginPermissions)

    subscribes_to: List[EventSubscription] = Field(default_factory=list)
    emits: List[EventEmission] = Field(default_factory=list)

    memory_contract: MemoryAccessContract = Field(default_factory=MemoryAccessContract)
    lineage_contract: LineageContract = Field(default_factory=LineageContract)

    auto_start: bool = False
    restart_policy: str = "never"
    health_check_endpoint: Optional[str] = None

    depends_on_plugins: List[str] = Field(default_factory=list)
    depends_on_capabilities: List[str] = Field(default_factory=list)

    @field_validator("version")
    @classmethod
    def version_must_be_semver(cls, v):
        Version(v)
        return v

    @field_validator("sdk_version_min", "sdk_version_max")
    @classmethod
    def sdk_version_must_be_semver(cls, v):
        if v is not None:
            Version(v)
        return v
