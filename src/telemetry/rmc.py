"""NMEA-0183 RMC (Recommended Minimum Specific GPS/Transit Data) parser."""

from dataclasses import dataclass
from typing import Optional

from src.core.error_tracking import global_error_tracker
from src.core.exceptions import (
    ChecksumMismatchError,
    FrameLengthError,
    InvalidPacketHeaderError,
)
from src.telemetry.nmea import NMEAParser


@dataclass(frozen=True)
class NMEARMCData:
    """Decoded GPRMC navigation fix dataset."""

    utc_time: str
    status: str
    latitude_deg: float
    longitude_deg: float
    speed_knots: float
    track_angle_deg: float
    date_str: str
    magnetic_variation_deg: Optional[float]


class RMCParser:
    """Parses standard ASCII NMEA RMC sentences."""

    @classmethod
    def parse_gprmc(cls, sentence: str) -> NMEARMCData:
        """Parses a $GPRMC / $GNRMC sentence into structured telemetry."""
        clean = sentence.strip()
        if not clean.startswith(("$GPRMC", "$GNRMC")):
            err = InvalidPacketHeaderError(f"Expected RMC header, got: {clean[:6]}")
            global_error_tracker.capture_exception(err, error_code="ERR_INVALID_HEADER")
            raise err

        if not NMEAParser.verify_checksum(clean):
            err_crc = ChecksumMismatchError("Invalid NMEA RMC checksum")
            global_error_tracker.capture_exception(err_crc, error_code="ERR_CHECKSUM_MISMATCH")
            raise err_crc

        payload = clean[1:].split("*")[0]
        fields = payload.split(",")

        if len(fields) < 12:
            err_len = FrameLengthError("Incomplete GPRMC sentence")
            global_error_tracker.capture_exception(err_len, error_code="ERR_FRAME_LENGTH")
            raise err_len

        utc_time = fields[1]
        status = fields[2]
        lat = NMEAParser._parse_coordinate(fields[3], fields[4])
        lon = NMEAParser._parse_coordinate(fields[5], fields[6])
        speed = float(fields[7]) if fields[7] else 0.0
        angle = float(fields[8]) if fields[8] else 0.0
        date_str = fields[9]

        mag_var: Optional[float] = None
        if len(fields) > 10 and fields[10]:
            mag_var = float(fields[10])
            if len(fields) > 11 and fields[11] == "W":
                mag_var = -mag_var

        return NMEARMCData(
            utc_time=utc_time,
            status=status,
            latitude_deg=lat,
            longitude_deg=lon,
            speed_knots=speed,
            track_angle_deg=angle,
            date_str=date_str,
            magnetic_variation_deg=mag_var,
        )
