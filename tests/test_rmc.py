import pytest

from src.core.exceptions import (
    ChecksumMismatchError,
    FrameLengthError,
    InvalidPacketHeaderError,
)
from src.telemetry.rmc import RMCParser


def test_valid_gprmc_parsing() -> None:
    sentence = "$GPRMC,220516,A,5133.82,N,00042.24,W,173.8,231.8,130694,004.2,W*70"
    data = RMCParser.parse_gprmc(sentence)

    assert data.utc_time == "220516"
    assert data.status == "A"
    assert pytest.approx(data.latitude_deg, abs=1e-4) == 51.5636667
    assert pytest.approx(data.longitude_deg, abs=1e-4) == -0.704
    assert data.speed_knots == 173.8
    assert data.track_angle_deg == 231.8
    assert data.date_str == "130694"
    assert data.magnetic_variation_deg == -4.2


def test_invalid_rmc_checksum() -> None:
    sentence = "$GPRMC,220516,A,5133.82,N,00042.24,W,173.8,231.8,130694,004.2,W*00"
    with pytest.raises(ChecksumMismatchError):
        RMCParser.parse_gprmc(sentence)


def test_invalid_rmc_header() -> None:
    sentence = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
    with pytest.raises(InvalidPacketHeaderError):
        RMCParser.parse_gprmc(sentence)


def test_truncated_rmc_sentence() -> None:
    # *08 is the valid XOR checksum for $GPRMC,220516,A
    sentence = "$GPRMC,220516,A*08"
    with pytest.raises(FrameLengthError):
        RMCParser.parse_gprmc(sentence)
