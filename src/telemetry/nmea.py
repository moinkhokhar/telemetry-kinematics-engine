"""NMEA-0183 navigation sentence decoder with checksum verification."""

from dataclasses import dataclass

from src.core.exceptions import (
    ChecksumMismatchError,
    FrameLengthError,
    InvalidPacketHeaderError,
)


@dataclass(frozen=True)
class NMEAGGAData:
    """Decoded GPGGA GPS Fix Data."""

    utc_time: str
    latitude_deg: float
    longitude_deg: float
    fix_quality: int
    num_satellites: int
    hdop: float
    altitude_m: float


class NMEAParser:
    """Decodes standard ASCII NMEA-0183 GPS navigation streams."""

    @staticmethod
    def verify_checksum(sentence: str) -> bool:
        """Verifies XOR checksum of standard NMEA string."""
        if not sentence.startswith("$") or "*" not in sentence:
            return False
        content, expected_hex = sentence[1:].split("*", 1)
        calculated = 0
        for char in content:
            calculated ^= ord(char)
        try:
            return calculated == int(expected_hex[:2], 16)
        except ValueError:
            return False

    @classmethod
    def _parse_coordinate(cls, raw_val: str, direction: str) -> float:
        """Converts NMEA DDMM.MMMM coordinate format to decimal degrees."""
        if not raw_val or not direction:
            return 0.0
        val = float(raw_val)
        degrees = int(val / 100)
        minutes = val - (degrees * 100)
        decimal = degrees + (minutes / 60.0)
        if direction in ["S", "W"]:
            decimal = -decimal
        return round(decimal, 7)

    @classmethod
    def parse_gpgga(cls, sentence: str) -> NMEAGGAData:
        """Parses a $GPGGA / $GNGGA sentence into structured geodetic telemetry."""
        clean_sentence = sentence.strip()
        if not clean_sentence.startswith(("$GPGGA", "$GNGGA")):
            raise InvalidPacketHeaderError(f"Expected GPGGA header, got: {clean_sentence[:6]}")
        if not cls.verify_checksum(clean_sentence):
            raise ChecksumMismatchError("Invalid NMEA checksum")

        payload = clean_sentence[1:].split("*")[0]
        fields = payload.split(",")

        if len(fields) < 10:
            raise FrameLengthError("Incomplete GPGGA sentence")

        utc_time = fields[1]
        lat = cls._parse_coordinate(fields[2], fields[3])
        lon = cls._parse_coordinate(fields[4], fields[5])
        fix_quality = int(fields[6]) if fields[6] else 0
        num_sats = int(fields[7]) if fields[7] else 0
        hdop = float(fields[8]) if fields[8] else 99.9
        alt = float(fields[9]) if fields[9] else 0.0

        return NMEAGGAData(
            utc_time=utc_time,
            latitude_deg=lat,
            longitude_deg=lon,
            fix_quality=fix_quality,
            num_satellites=num_sats,
            hdop=hdop,
            altitude_m=alt,
        )
