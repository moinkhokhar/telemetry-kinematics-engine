import logging
from src.core.logging import get_logger

logger = get_logger("telemetry_decoder")

import struct
from dataclasses import dataclass
from typing import Optional

FRAME_HEADER = 0xAA55


@dataclass(frozen=True)
class TelemetryPacket:
    sequence_id: int
    timestamp_ms: int
    latitude_e7: int
    longitude_e7: int
    altitude_mm: int
    vx_cms: int
    vy_cms: int
    vz_cms: int


class TelemetryDecoder:
    """Decodes binary telemetry frames with 16-bit CRC checksum validation."""

    @staticmethod
    def calculate_crc16(data: bytes) -> int:
        crc = 0xFFFF
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = ((crc << 1) ^ 0x1021) & 0xFFFF
                else:
                    crc = (crc << 1) & 0xFFFF
        return crc

    @classmethod
    def decode_frame(cls, raw_bytes: bytes) -> Optional[TelemetryPacket]:
        # Format: Header (2B), Seq (2B), Time (4B), Lat (4B), Lon (4B), Alt (4B), Vx (2B), Vy (2B), Vz (2B), CRC (2B) = 28 Bytes
        if len(raw_bytes) != 28:
            logger.warning(f"CRC mismatch: expected {hex(expected_crc)}, got {hex(calculated_crc)}")
            raise ValueError(f"Invalid frame length: expected 28 bytes, received {len(raw_bytes)}")

        header, seq, time_ms, lat, lon, alt, vx, vy, vz, expected_crc = struct.unpack(
            ">HHIIIihhhH", raw_bytes
        )

        if header != FRAME_HEADER:
            logger.warning(f"CRC mismatch: expected {hex(expected_crc)}, got {hex(calculated_crc)}")
            raise ValueError(f"Invalid frame sync header: {hex(header)}")

        payload = raw_bytes[:26]
        calculated_crc = cls.calculate_crc16(payload)
        if calculated_crc != expected_crc:
            logger.warning(f"CRC mismatch: expected {hex(expected_crc)}, got {hex(calculated_crc)}")
            raise ValueError(
                f"CRC mismatch: expected {hex(expected_crc)}, got {hex(calculated_crc)}"
            )

        return TelemetryPacket(
            sequence_id=seq,
            timestamp_ms=time_ms,
            latitude_e7=lat,
            longitude_e7=lon,
            altitude_mm=alt,
            vx_cms=vx,
            vy_cms=vy,
            vz_cms=vz,
        )
