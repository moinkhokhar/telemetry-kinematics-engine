import pytest
import struct
from src.telemetry.decoder import TelemetryDecoder, FRAME_HEADER

def test_valid_packet_decoding():
    payload = struct.pack(">HHIIIihhh", FRAME_HEADER, 101, 5000, 230000000, 720000000, 150000, 10, -5, 0)
    crc = TelemetryDecoder.calculate_crc16(payload)
    raw_packet = payload + struct.pack(">H", crc)

    packet = TelemetryDecoder.decode_frame(raw_packet)
    assert packet.sequence_id == 101
    assert packet.latitude_e7 == 230000000
    assert packet.vx_cms == 10

def test_corrupted_crc_rejection():
    payload = struct.pack(">HHIIIihhh", FRAME_HEADER, 1, 100, 0, 0, 0, 0, 0, 0)
    raw_packet = payload + struct.pack(">H", 0x1234)

    with pytest.raises(ValueError, match="CRC mismatch"):
        TelemetryDecoder.decode_frame(raw_packet)
