.PHONY: help install deps dev-deps test lint format clean build publish dev-install

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install the package using uv"
	@echo "  deps         - Install production dependencies (for CI)"
	@echo "  dev-deps     - Install development dependencies"
	@echo "  dev-install  - Install package in development mode with all dependencies"
	@echo "  test         - Run tests with pytest"
	@echo "  lint         - Run linters (ruff)"
	@echo "  format       - Format code with black"
	@echo "  clean        - Remove build artifacts and cache files"
	@echo "  build        - Build distribution packages"
	@echo "  publish      - Publish to PyPI using flit"

# Install package using uv
install:
	uv pip install -e .

# Install production dependencies (for CI/CD)
deps:
	pip install flit

# Install development dependencies using uv
dev-deps:
	uv pip install -e ".[dev]"

# Full development setup with uv
dev-install:
	@echo "Setting up development environment with uv..."
	uv venv
	uv pip install -e ".[dev]"
	@echo "Development environment ready! Activate with: source .venv/bin/activate"

# Run tests
test:
	uv run pytest

# Run linters
lint:
	uv run ruff check .
	uv run mypy fractal_specifications

# Format code
format:
	uv run black .
	uv run isort .
	uv run ruff check --fix .

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Build distribution packages
build: clean
	flit build

# Publish to PyPI (requires FLIT_USERNAME and FLIT_PASSWORD env vars)
publish: build
	flit publish
