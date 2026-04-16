from importlib import import_module

# The Single Source of Truth for the Beta Foundation
MODULE_MAP = {
    "system_tools": "tools.runtime.tools.system_tools",
    "ci_compiler": "tools.runtime.ci_compiler",
    "contract": "tools.runtime.contract",
    "kernel": "tools.runtime.kernel",
    "log": "tools.runtime.execution_log",
    "deps": "tools.runtime.deps",
    "engine": "tools.runtime.engine",
    "graph": "tools.runtime.graph",
    "manifest": "tools.runtime.manifest",
    "nodes": "tools.runtime.nodes",
    "replay": "tools.runtime.replay",
    "trace": "tools.runtime.trace",
}


def load(name: str):
    if name not in MODULE_MAP:
        raise ImportError(f"Module not registered in MODULE_MAP: {name}")
    return import_module(MODULE_MAP[name])


def validate():
    # Fail-fast mechanism for the CI Gate
    for name, path in MODULE_MAP.items():
        try:
            import_module(path)
        except ImportError as e:
            print(f"❌ FOUNDATION BREACH: Missing module {name} at {path}")
            raise e
