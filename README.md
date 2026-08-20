# Telemetry Kinematics & Estimation Engine

A high-performance Python engineering library for parsing binary and ASCII aerospace telemetry frames, computing conformal geodetic projections (WGS84, ECEF, UTM), and estimating multi-axis kinematics via discrete Kalman filtering.

## Architecture

```
src/
├── core/            # Domain exceptions, structured logging, stream metrics
├── estimation/      # 1D/2D Kinematic and 6-DOF Spatial Kalman Filters
├── telemetry/       # Binary frame & NMEA-0183 sentence parsers with CRC/Checksum verification
└── transforms/      # WGS84, ECEF Cartesian, and UTM coordinate projections
```

## Installation & Setup

```bash
git clone [https://github.com/moinkhokhar/telemetry-kinematics-engine.git](https://github.com/moinkhokhar/telemetry-kinematics-engine.git)
cd telemetry-kinematics-engine
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .
```

## Running Tests & Static Analysis

```bash
# Run test suite with coverage enforcement
pytest --cov=src --cov-report=term-missing --cov-fail-under=85

# Lint and type check
ruff check src tests
mypy src
```

## Running with Docker

```bash
docker compose up --build
```
