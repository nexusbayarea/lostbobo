import ast
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"

STDLIB = {
    "abc", "ast", "asyncio", "base64", "builtins", "collections", "contextlib",
    "copy", "csv", "dataclasses", "datetime", "decimal", "enum", "fnmatch",
    "functools", "glob", "hashlib", "hmac", "http", "importlib", "inspect",
    "io", "itertools", "json", "logging", "math", "multiprocessing", "operator",
    "os", "pathlib", "pickle", "platform", "pprint", "queue", "random", "re",
    "shutil", "signal", "socket", "sqlite3", "string", "struct", "subprocess",
    "sys", "tempfile", "textwrap", "threading", "time", "traceback", "types",
    "typing", "typing_extensions", "unittest", "urllib", "uuid", "warnings",
    "weakref", "xml", "zipfile", "zlib",
}

ALLOWED_THIRD_PARTY = {
    "fastapi", "pydantic", "uvicorn", "starlette", "requests", "httpx",
    "redis", "boto3", "botocore", "supabase", "postgrest", "jose",
    "passlib", "yaml", "toml", "dotenv", "PIL", "reportlab", "qrcode",
    "pandas", "numpy", "scipy", "torch", "runpod", "supervisor",
    "pytest", "ruff", "loguru", "structlog", "prometheus_client",
    "psycopg2", "asyncpg", "websockets", "tenacity", "orjson",
    "multipart", "anyio", "sniffio", "h11", "httpcore", "certifi",
    "charset_normalizer", "idna", "urllib3", "annotated_types",
    "pydantic_settings", "pydantic_core", "typing_inspection",
}

ALLOWED_INTERNAL = {
    "app", "runtime", "compiler", "services", "worker",
    "packages", "autoscaler", "skills", "tools", "infra",
    "backend",
}

VIOLATIONS = []


def is_violation(module: str) -> bool:
    root = module.split(".")[0]
    if root in STDLIB:
        return False
    if root in ALLOWED_THIRD_PARTY:
        return False
    if root in ALLOWED_INTERNAL:
        return False
    return True


def scan_file(path: Path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except Exception as e:
        print(f"Warning: Could not parse {path}: {e}")
        return

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and is_violation(node.module):
                VIOLATIONS.append((str(path), node.module, "ImportFrom"))
        if isinstance(node, ast.Import):
            for n in node.names:
                if is_violation(n.name):
                    VIOLATIONS.append((str(path), n.name, "Import"))


def scan():
    for base, _, files in os.walk(BACKEND):
        base_path = Path(base)
        # Skip virtual envs, caches, and test fixtures
        if any(p in str(base_path) for p in [".venv", "__pycache__", ".mypy_cache", "node_modules"]):
            continue
        for f in files:
            if f.endswith(".py"):
                scan_file(base_path / f)


if __name__ == "__main__":
    scan()
    if VIOLATIONS:
        print("\nRUNTIME ISOLATION VIOLATIONS:\n")
        for v in VIOLATIONS:
            print(f" - {v[0]} → {v[1]} ({v[2]})")
        sys.exit(1)
    print("Runtime isolation OK")
