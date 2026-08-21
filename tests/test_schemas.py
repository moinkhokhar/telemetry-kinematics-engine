import pytest
from pydantic import ValidationError

from src.telemetry.schemas import NMEAGGASchema, TelemetryFrameSchema


def test_valid_telemetry_frame_schema():
    frame = TelemetryFrameSchema(
        sequence_id=10,
        timestamp_ms=1000,
        latitude_e7=450000000,
        longitude_e7=90000000,
        altitude_mm=500000,
        vx_cms=100,
        vy_cms=-50,
        vz_cms=0,
    )
    assert frame.sequence_id == 10


def test_invalid_telemetry_frame_bounds():
    with pytest.raises(ValidationError):
        TelemetryFrameSchema(
            sequence_id=-1,  # Invalid: negative
            timestamp_ms=1000,
            latitude_e7=1000000000,  # Invalid: > 90 deg
            longitude_e7=0,
            altitude_mm=0,
            vx_cms=0,
            vy_cms=0,
            vz_cms=0,
        )


def test_valid_nmea_schema():
    nmea = NMEAGGASchema(
        utc_time="123519",
        latitude_deg=48.1173,
        longitude_deg=11.5166,
        fix_quality=1,
        num_satellites=8,
        hdop=0.9,
        altitude_m=545.4,
    )
    assert nmea.fix_quality == 1


def test_invalid_nmea_schema():
    with pytest.raises(ValidationError):
        NMEAGGASchema(
            utc_time="INVALID",
            latitude_deg=95.0,  # Out of bounds
            longitude_deg=0.0,
            fix_quality=1,
            num_satellites=8,
            hdop=0.9,
            altitude_m=10.0,
        )
