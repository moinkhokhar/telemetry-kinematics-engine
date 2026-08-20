# Contributing to Telemetry Kinematics Engine

## Development Setup
1. Clone the repository: `git clone https://github.com/moinkhokhar/telemetry-kinematics-engine.git`
2. Create and activate virtual environment: `python3 -m venv venv && source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt -r requirements-dev.txt`
4. Install local package in editable mode: `pip install -e .`

## Quality Standards
- All code must pass `ruff check src tests` and `mypy src`.
- Maintain test coverage above 85% with `pytest --cov=src --cov-fail-under=85`.
