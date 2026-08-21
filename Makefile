.PHONY: help lock install test lint format clean

help:
	@echo "Available targets:"
	@echo "  lock    - Recompile dependency lockfiles using pip-compile"
	@echo "  install - Install locked production and dev dependencies"
	@echo "  test    - Run pytest test suite with coverage enforcement"
	@echo "  lint    - Run ruff and mypy static checks"
	@echo "  format  - Auto-format code with ruff"

lock:
	pip-compile requirements.in -o requirements.txt
	pip-compile requirements-dev.in -o requirements-dev.txt

install:
	pip install -r requirements.txt -r requirements-dev.txt
	pip install -e .

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
	rm -rf .coverage htmlcov
