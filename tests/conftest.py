"""Global pytest fixtures and test vector isolation."""

import pytest
from src.transforms.geodetic import GeodeticPoint


@pytest.fixture
def london_waypoint() -> GeodeticPoint:
    """Standardized geodetic test waypoint (London Heathrow)."""
    return GeodeticPoint(latitude_deg=51.4700, longitude_deg=-0.4543, altitude_m=25.0)


@pytest.fixture
def paris_waypoint() -> GeodeticPoint:
    """Standardized geodetic test waypoint (Paris Charles de Gaulle)."""
    return GeodeticPoint(latitude_deg=49.0097, longitude_deg=2.5479, altitude_m=119.0)


@pytest.fixture
def sample_binary_frame_payload() -> bytes:
    """Valid binary telemetry packet bytes (28 bytes)."""
    import struct
    from src.telemetry.decoder import FRAME_HEADER, TelemetryDecoder

    payload = struct.pack(
        ">HHIIIihhh", FRAME_HEADER, 201, 10000, 230000000, 720000000, 150000, 100, -50, 0
    )
    crc = TelemetryDecoder.calculate_crc16(payload)
    return payload + struct.pack(">H", crc)
