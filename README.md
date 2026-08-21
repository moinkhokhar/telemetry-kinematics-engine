# Telemetry Kinematics & Estimation Engine

[![Continuous Integration](https://github.com/moinkhokhar/telemetry-kinematics-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/moinkhokhar/telemetry-kinematics-engine/actions)
![Python 3.10 | 3.11 | 3.12](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen)

A production-grade Python engineering framework for decoding high-frequency aerospace telemetry (Binary frames & NMEA-0183 sentences), conformal geodetic projections (WGS84, ECEF, UTM), spherical navigation (Bearings, Cross-Track Distance), and 6-DOF spatial state estimation via discrete Kalman filtering.

## Architecture Overview

```text
       +-------------------------------------------------------------+
       |                  Raw Telemetry Ingestion                    |
       |     [Binary Frame Decoder]        [NMEA-0183 Parser]        |
       +-----------------------------+-------------------------------+
                                     | (Pydantic Validation Models)
                                     v
       +-------------------------------------------------------------+
       |               Coordinate Transformations                    |
       |  [WGS84 -> ECEF]   [ECEF -> WGS84]   [WGS84 -> UTM Zone]    |
       |             [Spherical Great-Circle Geodesy]                |
       +-----------------------------+-------------------------------+
                                     | (Cartesian Spatial Vectors)
                                     v
       +-------------------------------------------------------------+
       |             6-DOF Kinematic Estimation Engine               |
       |   [Spatial Kalman Filter (EKF)]   [Quaternion Attitude DCM] |
       +-----------------------------+-------------------------------+
                                     |
                                     v
       +-------------------------------------------------------------+
       |             Operational Health & API Observability          |
       |   [Stream Metrics]    [dictConfig Logging]    [GET /health] |
       +-------------------------------------------------------------+
```

## Directory Structure

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
git clone [https://github.com/moinkhokhar/telemetry-kinematics-engine.git](https://github.com/moinkhokhar/telemetry-kinematics-engine.git)
cd telemetry-kinematics-engine
python3 -m venv venv
source venv/bin/activate
make install
```

## Testing & Quality Gates

```bash
make test
make lint
```

## Infrastructure & Deployment

```bash
docker compose up --build
cd infra/terraform && terraform init -backend=false && terraform validate
```
