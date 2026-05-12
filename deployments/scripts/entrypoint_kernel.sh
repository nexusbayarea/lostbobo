#!/bin/bash
set -e

echo "SimHPC Kernel booting..."

python3 deployments/runtime/bootstrap/infisical_bootstrap.py

exec python3 -m backend.runtime.kernel_boot
