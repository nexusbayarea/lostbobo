CI_DAG = [
    {"id": "env", "cmd": "python tools/env_bootstrap.py ci", "name": "Bootstrap Environment"},
    {"id": "lint", "cmd": "python -m ruff check .", "name": "Ruff Lint"},
    {"id": "format", "cmd": "python -m ruff format . --check", "name": "Ruff Format Check"},
    {"id": "imports", "cmd": "python -c 'from app.gateway import app; from worker.worker import worker; print(\"imports OK\")'", "name": "Import Check"},
    {"id": "isolation", "cmd": "python ../tools/ci_gates/runtime_isolation.py", "name": "Runtime Isolation Gate"},
    {"id": "tests", "cmd": "python3 -m pytest -q --tb=short ../tests/", "name": "Tests"},
]
