import pytest

from src.core.exceptions import FrameLengthError, InvalidPacketHeaderError
from src.telemetry.decoder import TelemetryDecoder
from src.telemetry.nmea import NMEAParser


def test_decoder_rejects_short_frames() -> None:
    short_payload = b"\xaa\x55\x00\x01\x00\x00"
    with pytest.raises(ValueError, match="Invalid frame length"):
        TelemetryDecoder.decode_frame(short_payload)


def test_decoder_rejects_corrupted_sync_header() -> None:
    invalid_header = b"\xff\xff" + b"\x00" * 26
    with pytest.raises(ValueError, match="Invalid frame sync header"):
        TelemetryDecoder.decode_frame(invalid_header)


def test_nmea_rejects_truncated_sentence() -> None:
    sentence = "$GPGGA,123519,4807.038*45"
    with pytest.raises(FrameLengthError):
        NMEAParser.parse_gpgga(sentence)


def test_nmea_rejects_unrecognized_header() -> None:
    invalid_header = "$INVALID,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
    with pytest.raises(InvalidPacketHeaderError):
        NMEAParser.parse_gpgga(invalid_header)
