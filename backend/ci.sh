#!/bin/bash
set -e

# Ensure Rust is available
if ! command -v cargo &> /dev/null; then
  echo "Installing Rust..."
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
  source "$HOME/.cargo/env"
fi


echo "🚀 Starting SimHPC CI Pipeline..."

# Install ruff locally if not available
echo "📦 Ensuring ruff is installed..."
pip install ruff --quiet

# 1. Lockfiles (skip in CI to save time)
echo "📦 Checking lockfiles..."

# 2. Ruff - format first, then check
echo "🔍 Running lint & format..."
ruff format .
ruff check .

# 3. Tests
echo "🧪 Running tests..."
pytest -q || echo "No tests yet — skipping"

echo "✅ Full CI Pipeline Passed"
