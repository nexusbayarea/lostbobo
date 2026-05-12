#!/bin/bash
set -e

echo "SimHPC GPU Worker booting..."

python3 deployments/runtime/bootstrap/infisical_bootstrap.py

exec python3 -m backend.runtime.gpu_worker
