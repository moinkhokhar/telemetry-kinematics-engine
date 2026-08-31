"""End-to-end telemetry processing pipeline."""

from dataclasses import dataclass
from typing import Any, Callable, Optional, Union, cast

import numpy as np

from src.core.error_tracking import ErrorTracker, global_error_tracker
from src.core.exceptions import (
    ChecksumMismatchError,
    FrameLengthError,
    InvalidPacketHeaderError,
)
from src.core.logging import get_logger
from src.core.metrics import StreamMetrics
from src.estimation.ekf_3d import SpatialKalmanFilter
from src.telemetry.decoder import TelemetryDecoder, TelemetryPacket
from src.telemetry.nmea import NMEAGGAData, NMEAParser
from src.telemetry.rmc import NMEARMCData, RMCParser
from src.transforms.geodetic import CoordinateTransformer, GeodeticPoint

logger = get_logger("telemetry_pipeline")

BinaryOrNMEA = Union[TelemetryPacket, NMEAGGAData, NMEARMCData]
FrameHandler = Callable[[BinaryOrNMEA, Optional[dict[str, Any]], Optional[dict[str, Any]]], None]


@dataclass
class PipelineResult:
    """Result of processing a single telemetry input."""

    success: bool
    data: Optional[BinaryOrNMEA] = None
    error: Optional[Exception] = None
    error_type: Optional[str] = None
    transformed: Optional[dict[str, Any]] = None
    estimated: Optional[dict[str, Any]] = None


class TelemetryPipeline:
    """Orchestrates end-to-end telemetry decoding, transformation, and estimation."""

    def __init__(
        self,
        metrics: Optional[StreamMetrics] = None,
        error_tracker: Optional[ErrorTracker] = None,
        enable_transforms: bool = True,
        enable_estimation: bool = True,
    ) -> None:
        self.metrics = metrics or StreamMetrics()
        self.error_tracker = error_tracker or global_error_tracker
        self.enable_transforms = enable_transforms
        self.enable_estimation = enable_estimation
        self._ekf = SpatialKalmanFilter() if enable_estimation else None
        self._frame_handler: Optional[FrameHandler] = None

    def set_frame_handler(self, handler: FrameHandler) -> None:
        """Registers a callback invoked after each successfully processed frame."""
        self._frame_handler = handler

    def process_binary_frame(self, raw_bytes: bytes) -> PipelineResult:
        """Decode a binary telemetry frame and run it through the pipeline."""
        try:
            packet = TelemetryDecoder.decode_frame(raw_bytes)
        except Exception as exc:
            self._record_binary_error(packet=None, exc=exc)
            return PipelineResult(success=False, error=exc)

        packet = cast(TelemetryPacket, packet)
        self.metrics.record_frame(sequence_id=packet.sequence_id, is_valid=True)
        transformed = self._transform_binary(packet)
        estimated = self._estimate_position(packet, transformed)
        result = PipelineResult(
            success=True,
            data=packet,
            transformed=transformed,
            estimated=estimated,
        )
        self._invoke_handler(packet, transformed, estimated)
        return result

    def process_nmea_sentence(self, sentence: str) -> PipelineResult:
        """Decode an NMEA sentence and run it through the pipeline."""
        clean = sentence.strip()
        data: BinaryOrNMEA
        try:
            if clean.startswith(("$GPGGA", "$GNGGA")):
                data = NMEAParser.parse_gpgga(clean)
            elif clean.startswith(("$GPRMC", "$GNRMC")):
                data = RMCParser.parse_gprmc(clean)
            else:
                raise ValueError(f"Unsupported NMEA sentence: {clean[:6]}")
        except Exception as exc:
            self._record_nmea_error(clean, exc)
            return PipelineResult(success=False, error=exc)

        self.metrics.record_nmea_frame(is_valid=True)
        transformed = self._transform_nmea(data)
        estimated = self._estimate_position(data, transformed)
        result = PipelineResult(
            success=True,
            data=data,
            transformed=transformed,
            estimated=estimated,
        )
        self._invoke_handler(data, transformed, estimated)
        return result

    def process(self, data: Union[bytes, str]) -> PipelineResult:
        """Auto-detect input type and route to the appropriate decoder."""
        if isinstance(data, str):
            return self.process_nmea_sentence(data)
        if self._is_nmea_bytes(data):
            return self.process_nmea_sentence(data.decode("ascii"))
        return self.process_binary_frame(data)

    @staticmethod
    def _is_nmea_bytes(data: bytes) -> bool:
        """Detects whether raw bytes contain an ASCII NMEA sentence."""
        if not data:
            return False
        if data[0:1] != b"$":
            return False
        try:
            data.decode("ascii")
        except UnicodeDecodeError:
            return False
        return True

    def _transform_binary(self, packet: TelemetryPacket) -> Optional[dict[str, Any]]:
        """Convert binary packet geodetic fields to ECEF."""
        return self._transform_coordinates(
            latitude_deg=packet.latitude_e7 / 1e7,
            longitude_deg=packet.longitude_e7 / 1e7,
            altitude_m=packet.altitude_mm / 1000.0,
        )

    def _transform_nmea(self, data: BinaryOrNMEA) -> Optional[dict[str, Any]]:
        """Convert NMEA geodetic fields to ECEF."""
        altitude = getattr(data, "altitude_m", 0.0)
        latitude_deg = getattr(data, "latitude_deg", 0.0)
        longitude_deg = getattr(data, "longitude_deg", 0.0)
        return self._transform_coordinates(
            latitude_deg=latitude_deg,
            longitude_deg=longitude_deg,
            altitude_m=altitude,
        )

    def _transform_coordinates(
        self, latitude_deg: float, longitude_deg: float, altitude_m: float
    ) -> Optional[dict[str, Any]]:
        """Shared coordinate transformation logic."""
        if not self.enable_transforms:
            return None
        try:
            geodetic = GeodeticPoint(
                latitude_deg=latitude_deg,
                longitude_deg=longitude_deg,
                altitude_m=altitude_m,
            )
            ecef = CoordinateTransformer.geodetic_to_ecef(geodetic)
            return {"geodetic": geodetic, "ecef": ecef}
        except Exception as exc:
            logger.warning("Coordinate transformation failed: %s", exc)
            return None

    def _estimate_position(
        self, data: BinaryOrNMEA, transformed: Optional[dict[str, Any]]
    ) -> Optional[dict[str, Any]]:
        """Fuse transformed position through the EKF when available."""
        if not self.enable_estimation or not transformed or not self._ekf:
            return None
        try:
            ecef = transformed["ecef"]
            pos = np.array([ecef.x_m, ecef.y_m, ecef.z_m], dtype=np.float64)
            self._ekf.predict()
            self._ekf.update(pos)
            return {
                "position": self._ekf.estimated_position,
                "velocity": self._ekf.estimated_velocity,
            }
        except Exception as exc:
            logger.warning("State estimation failed: %s", exc)
            return None

    def _record_binary_error(self, packet: Optional[TelemetryPacket], exc: Exception) -> None:
        """Record binary decoding failures in metrics and error tracker."""
        error_type: Optional[str] = "header"
        msg = str(exc)
        if "CRC mismatch" in msg:
            error_type = "crc"
        elif "frame length" in msg.lower():
            error_type = None

        self.metrics.total_frames_received += 1
        if error_type == "crc":
            self.metrics.crc_errors += 1
        elif error_type == "header":
            self.metrics.invalid_headers += 1

        self.error_tracker.capture_exception(exc, error_code="ERR_PIPELINE_BINARY")

    def _record_nmea_error(self, sentence: str, exc: Exception) -> None:
        """Record NMEA parsing failures in metrics and error tracker."""
        if isinstance(exc, ChecksumMismatchError):
            self.metrics.record_nmea_frame(is_valid=False, error_type="crc")
            self.error_tracker.capture_exception(exc, error_code="ERR_NMEA_CHECKSUM")
        elif isinstance(exc, InvalidPacketHeaderError):
            self.metrics.record_nmea_frame(is_valid=False, error_type="header")
            self.error_tracker.capture_exception(exc, error_code="ERR_NMEA_HEADER")
        elif isinstance(exc, FrameLengthError):
            self.metrics.record_nmea_frame(is_valid=False)
            self.error_tracker.capture_exception(exc, error_code="ERR_NMEA_LENGTH")
        else:
            self.metrics.record_nmea_frame(is_valid=False)
            self.error_tracker.capture_exception(exc, error_code="ERR_NMEA_PARSE")

    def _invoke_handler(
        self,
        data: BinaryOrNMEA,
        transformed: Optional[dict[str, Any]],
        estimated: Optional[dict[str, Any]],
    ) -> None:
        """Calls the registered frame handler if one is set."""
        if self._frame_handler:
            try:
                self._frame_handler(data, transformed, estimated)
            except Exception as exc:
                logger.error("Frame handler failed: %s", exc)
