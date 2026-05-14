"""
SimHPC Plugin SDK — Public API for plugin developers.

Version: 1.0.0
"""

SDK_VERSION = "1.0.0"

# Manifest & Contracts
from backend.core.sdk.abi.plugin_manifest import (
    PluginManifest,
    IsolationTier,
    GPUProfile,
    ResourceQuota,
    PluginPermissions,
    SyscallPermission,
    NetworkEgressRule,
    SecretScope,
    DAGNodeDeclaration,
    EventSubscription,
    EventEmission,
    MemoryAccessContract,
    LineageContract,
    PluginPermission,
    PluginPassport,
)

# Base Plugin
from backend.core.sdk.base_plugin import BasePlugin

# Lifecycle
from backend.core.sdk.abi.lifecycle import PluginState, LifecycleManager, LifecycleEvent

# Permissions
from backend.core.sdk.abi.permissions import Syscall, PermissionSet

__all__ = [
    "SDK_VERSION",
    "PluginManifest",
    "BasePlugin",
    "IsolationTier",
    "GPUProfile",
    "ResourceQuota",
    "PluginPermissions",
    "SyscallPermission",
    "NetworkEgressRule",
    "SecretScope",
    "DAGNodeDeclaration",
    "EventSubscription",
    "EventEmission",
    "MemoryAccessContract",
    "LineageContract",
    "PluginPermission",
    "PluginPassport",
    "PluginState",
    "LifecycleManager",
    "LifecycleEvent",
    "Syscall",
    "PermissionSet",
]
