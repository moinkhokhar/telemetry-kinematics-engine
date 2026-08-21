# Telemetry Kinematics & Estimation Engine

A production-grade Python engineering framework for parsing aerospace telemetry (Binary frames & NMEA-0183 sentences), conformal geodetic projections (WGS84, ECEF, UTM), spherical navigation (Bearings, Cross-Track Distance), and 6-DOF spatial state estimation via discrete Kalman filtering.

## Architecture Overview

```text
src/
├── api/             # HTTP health monitoring probes and status telemetry
├── core/            # Error tracker diagnostics, structured logging, stream metrics
├── estimation/      # 6-DOF Spatial Kalman filter and Quaternion kinematics
├── telemetry/       # Binary frame & NMEA (GGA, RMC) decoders with Pydantic validation
└── transforms/      # WGS84, ECEF, Bowring Inverse, UTM, and Geodesy engines

infra/
├── k8s/             # Kubernetes worker deployment and service manifests
└── terraform/       # Reusable AWS ECR Terraform modules and state configuration
```

## Environment Configuration

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `LOG_LEVEL` | String | `INFO` | Logging threshold (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `STREAM_BUFFER_SIZE` | Integer | `65536` | Ingestion socket ring buffer allocation in bytes |
| `TELEMETRY_PORT` | Integer | `50051` | Default listening port for UDP/TCP telemetry streams |

## Installation & Local Setup

```bash
# Clone repository and configure virtual environment
git clone [https://github.com/moinkhokhar/telemetry-kinematics-engine.git](https://github.com/moinkhokhar/telemetry-kinematics-engine.git)
cd telemetry-kinematics-engine
python3 -m venv venv
source venv/bin/activate

# Install dependencies using pinned lockfiles
make install
```

## Testing & Code Quality Gates

```bash
# Run complete test suite with 85% coverage enforcement
make test

# Execute strict typing and linter checks
make lint
```

## Infrastructure & Container Deployment

```bash
# Build and run self-contained test suite via Docker Compose
docker compose up --build

# Validate Terraform modules
cd infra/terraform && terraform init && terraform validate
```
