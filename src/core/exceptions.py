"""Custom domain exceptions for telemetry kinematics and state estimation."""


class TelemetryEngineError(ValueError):
    """Base exception for all telemetry engine errors."""


class ChecksumMismatchError(TelemetryEngineError):
    """Raised when frame CRC or checksum verification fails."""


class InvalidPacketHeaderError(TelemetryEngineError):
    """Raised when an unrecognized frame synchronization header is received."""


class FrameLengthError(TelemetryEngineError):
    """Raised when payload buffer does not match expected wire byte size."""


class FilterDivergenceError(TelemetryEngineError):
    """Raised when covariance matrix diverges or becomes non-invertible."""


class CoordinateOutOfBoundsError(TelemetryEngineError):
    """Raised when geodetic coordinates fall outside physical ellipsoidal bounds."""
