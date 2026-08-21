#!/bin/bash
set -e
echo "Running test suite in isolated container..."
pytest --cov=src --cov-report=term-missing --cov-fail-under=85
