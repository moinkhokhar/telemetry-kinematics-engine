"""Pydantic validation schemas for raw and decoded telemetry data."""

from pydantic import BaseModel, Field, field_validator


class TelemetryFrameSchema(BaseModel):
    """Strict schema for decoded binary aerospace telemetry frames."""

    sequence_id: int = Field(ge=0, le=65535, description="16-bit monotonic sequence counter")
    timestamp_ms: int = Field(ge=0, description="Millisecond timestamp since epoch")
    latitude_e7: int = Field(ge=-900000000, le=900000000, description="Latitude scaled by 1e7")
    longitude_e7: int = Field(ge=-1800000000, le=1800000000, description="Longitude scaled by 1e7")
    altitude_mm: int = Field(ge=-1000000, le=100000000, description="Ellipsoidal altitude in mm")
    vx_cms: int = Field(ge=-50000, le=50000, description="X velocity in cm/s")
    vy_cms: int = Field(ge=-50000, le=50000, description="Y velocity in cm/s")
    vz_cms: int = Field(ge=-50000, le=50000, description="Z velocity in cm/s")


class NMEAGGASchema(BaseModel):
    """Strict schema for NMEA-0183 GPGGA navigation sentences."""

    utc_time: str = Field(min_length=6, max_length=10, description="UTC time string HHMMSS")
    latitude_deg: float = Field(
        ge=-90.0, le=90.0, description="Geodetic latitude in decimal degrees"
    )
    longitude_deg: float = Field(
        ge=-180.0, le=180.0, description="Geodetic longitude in decimal degrees"
    )
    fix_quality: int = Field(ge=0, le=8, description="GPS fix quality indicator")
    num_satellites: int = Field(ge=0, le=64, description="Satellites in view")
    hdop: float = Field(ge=0.0, le=99.9, description="Horizontal dilution of precision")
    altitude_m: float = Field(
        ge=-1000.0, le=100000.0, description="Antenna altitude above mean sea level"
    )

    @field_validator("utc_time")
    @classmethod
    def validate_utc_format(cls, v: str) -> str:
        if not v.replace(".", "").isdigit():
            raise ValueError("UTC time must contain only numeric characters")
        return v
