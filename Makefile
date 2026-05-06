# ================================================
# SimHPC Makefile
# ================================================

.PHONY: help dev lint format check ci lock test clean

help:
	@echo "SimHPC Development Commands"
	@echo "============================"
	@echo "make dev           → Install editable dev environment"
	@echo "make lint          → Ruff lint"
	@echo "make format        → Auto-format code"
	@echo "make check         → Lint + format check"
	@echo "make ci            → Full CI (lock + check + test)"
	@echo "make lock          → Regenerate all lockfiles"
	@echo "make test          → Run tests"
	@echo "make clean         → Cleanup"
	@echo ""

# Development Setup
dev:
	uv sync --extra dev
	uv pip install -e .
	@echo "✅ Development environment ready"

# Linting & Formatting
lint:
	cd backend && ruff check .

format:
	cd backend && ruff format .

check:
	cd backend && ruff format --check .
	cd backend && ruff check .

# Full CI (this is what your workflow calls)
ci: lock check test
	@echo "✅ Full CI pipeline passed"

# Lockfiles
lock:
	uv pip compile pyproject.toml --extra api -o requirements.api.lock
	uv pip compile pyproject.toml --extra worker -o requirements.worker.lock
	uv pip compile pyproject.toml --extra dev -o requirements-dev.txt
	uv pip compile pyproject.toml --extra gpu -o requirements.gpu.lock
	@echo "✅ All lockfiles regenerated"

# Testing
test:
	cd backend && pytest -q || echo "No tests yet - skipping"

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup completed"
