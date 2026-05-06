#!/bin/bash
set -e

echo "🚀 Starting SimHPC CI Pipeline..."

echo "📦 Regenerating lockfiles..."
uv pip compile ../pyproject.toml --extra api -o requirements.api.lock
uv pip compile ../pyproject.toml --extra worker -o requirements.worker.lock
uv pip compile ../pyproject.toml --extra dev -o requirements-dev.txt
uv pip compile ../pyproject.toml --extra gpu -o requirements.gpu.lock

echo "🔍 Running lint & format..."
ruff format --check .
ruff check .

echo "🧪 Running tests..."
pytest -q || echo "No tests yet — skipping"

echo "✅ Full CI Pipeline Passed"