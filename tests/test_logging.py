import logging
import struct
import pytest
from src.telemetry.decoder import TelemetryDecoder, FRAME_HEADER

def test_decoder_emits_warning_on_bad_crc(caplog):
    payload = struct.pack(">HHIIIihhh", FRAME_HEADER, 1, 100, 0, 0, 0, 0, 0, 0)
    raw_packet = payload + struct.pack(">H", 0x1234)

    with caplog.at_level(logging.WARNING):
        with pytest.raises(ValueError):
            TelemetryDecoder.decode_frame(raw_packet)
            
    assert "CRC mismatch" in caplog.text
