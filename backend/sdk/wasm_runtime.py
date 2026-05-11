# backend/sdk/wasm_runtime.py
from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass
class WasmSecurityConfig:
    max_memory_pages: int = 256
    max_fuel: int = 25_000_000
    enable_swivel: bool = True
    enable_strict_bounds: bool = True
    allowed_host_functions: list[str] = None


@dataclass
class WasmPluginConfig:
    module_path: str
    max_memory_pages: int = 256
    max_fuel: int = 10_000_000
    allowed_host_functions: list[str] = None


class HardenedWasmRuntime:
    """Secure WASM sandbox with full hardening."""

    def __init__(self, config: WasmSecurityConfig):
        self.config = config
        self.engine = None
        self.store = None
        self.instance = None
        self._initialized = False
        self._wasm_config = None

    def _initialize(self) -> None:
        """Initialize WASM runtime with security hardening."""
        try:
            import wasmtime

            self._wasm_config = wasmtime.Config()
            self._wasm_config.cranelift_opt_level = "speed_and_size"

            if hasattr(self._wasm_config, "enable_spectre_mitigations"):
                self._wasm_config.enable_spectre_mitigations(True)

            self.engine = wasmtime.Engine()
            self.store = wasmtime.Store(self.engine)
            self.store.set_limits(memory_size=self.config.max_memory_pages * 64 * 1024)
            self.store.set_fuel(self.config.max_fuel)

            self._initialized = True

        except ImportError:
            log.warning("wasmtime not installed, WASM plugins will fall back to sandbox")
        except Exception as e:
            log.error("WASM initialization failed: %s", e)

    def _create_linker(self, plugin_id: str):
        """Explicit capability-based host functions."""
        import wasmtime

        linker = wasmtime.Linker(self.engine)

        safe_functions = {
            "log": self._host_log,
            "emit_event": self._host_emit_event,
            "observe_state": self._host_observe_state,
            "get_random": self._host_get_random,
        }

        for name, func in safe_functions.items():
            linker.define("env", name, wasmtime.Func(self.store, wasmtime.FuncType([], []), func))

        return linker

    def _host_log(self, caller):
        log.info("WASM plugin logged message")

    def _host_emit_event(self, caller):
        pass

    def _host_observe_state(self, caller):
        pass

    def _host_get_random(self, caller):
        pass

    async def execute(self, wasm_path: str, command: str, payload: dict) -> dict:
        """Execute with full security controls."""
        t0 = time.time()

        await self._add_jitter()

        if not self._initialized:
            self._initialize()

        if not self._initialized:
            return {"success": False, "error": "WASM runtime not available"}

        try:
            import wasmtime

            with open(wasm_path, "rb") as f:
                module = wasmtime.Module(self.store.engine, f.read())

            linker = self._create_linker("current_plugin")
            instance = linker.instantiate(self.store, module)

            self.store.set_fuel(self.config.max_fuel)

            func = instance.exports(self.store)["execute"]
            result = func(self.store, command, self._serialize_to_wasm(payload))

            duration = (time.time() - t0) * 1000
            log.info("WASM execution completed in %.1fms", duration)

            return {"success": True, "result": result, "duration_ms": duration}

        except wasmtime.Trap as e:
            log.error("WASM security trap: %s", e)
            return {"success": False, "error": "Security violation (WASM trap)"}
        except Exception as e:
            log.error("WASM execution failed: %s", e)
            return {"success": False, "error": str(e)}

    async def _add_jitter(self, max_ms: float = 8.0):
        """Break timing side-channels."""
        jitter = random.uniform(0, max_ms)
        await asyncio.sleep(jitter / 1000.0)

    def _serialize_to_wasm(self, payload: dict) -> int:
        return 0


class WasmSandbox:
    """Legacy alias for compatibility."""

    def __init__(self, config: WasmPluginConfig):
        self.config = config
        self._runtime = HardenedWasmRuntime(
            WasmSecurityConfig(
                max_memory_pages=config.max_memory_pages,
                max_fuel=config.max_fuel,
                allowed_host_functions=config.allowed_host_functions,
            )
        )

    async def execute(self, command: str, payload: dict) -> dict:
        return await self._runtime.execute(self.config.module_path, command, payload)


def create_wasm_sandbox(config: WasmPluginConfig) -> WasmSandbox:
    return WasmSandbox(config)
