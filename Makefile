.PHONY: help install test lint format clean

help:
	@echo "Available targets:"
	@echo "  install - Install locked dependencies via poetry"
	@echo "  test    - Run pytest test suite with coverage enforcement"
	@echo "  lint    - Run ruff and mypy static analysis"
	@echo "  format  - Auto-format code using ruff"
	@echo "  clean   - Remove build artifacts and caches"

install:
	pip install poetry
	poetry install

test:
	pytest --cov=src --cov-report=term-missing --cov-fail-under=85

lint:
	ruff check src tests
	mypy src

format:
	ruff check src tests --fix
	ruff format src tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf .coverage htmlcov dist build
