import pytest

from src.core.exceptions import (
    ChecksumMismatchError,
    FrameLengthError,
    InvalidPacketHeaderError,
)
from src.telemetry.nmea import NMEAParser


def test_valid_gpgga_decoding():
    sentence = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
    data = NMEAParser.parse_gpgga(sentence)

    assert data.utc_time == "123519"
    assert pytest.approx(data.latitude_deg, abs=1e-4) == 48.1173
    assert pytest.approx(data.longitude_deg, abs=1e-4) == 11.5166
    assert data.fix_quality == 1
    assert data.num_satellites == 8
    assert data.altitude_m == 545.4


def test_corrupt_nmea_checksum():
    sentence = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*00"
    with pytest.raises(ChecksumMismatchError):
        NMEAParser.parse_gpgga(sentence)


def test_invalid_nmea_header():
    sentence = "$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A"
    with pytest.raises(InvalidPacketHeaderError):
        NMEAParser.parse_gpgga(sentence)


def test_truncated_nmea_payload():
    # *45 is the correct XOR checksum for "$GPGGA,123519,4807.038"
    sentence = "$GPGGA,123519,4807.038*45"
    with pytest.raises(FrameLengthError):
        NMEAParser.parse_gpgga(sentence)
