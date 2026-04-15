# SimHPC Progress

## April 14, 2026

### Fixed: src layout and CI workflow

- **pyproject.toml**: 
  - Added `src = ["src"]` to ruff config
  - Added `packages = ["app", "worker"]` to setuptools
  - Fixed `license = { text = "MIT" }`
  - Added `uv>=0.4.0` to dev/ci deps
  
- **dag-ci.yml**:
  - Changed lint to `src/ tests/ tools/` paths
  - Changed tests to check `src/app/ src/worker/ tests/ tools/`
  - Added explicit pytest run in tests job
  - Added boot validation, fail-fast, drift check, DAG tests to api-ci

All tests pass locally:
```
[System Contract] -> DAG Validation
[PASS]
[System Contract] -> Runtime Contract
[PASS]
[System Contract] -> Trace Validation
[PASS]
[SYSTEM CONTRACT PASSED]
```