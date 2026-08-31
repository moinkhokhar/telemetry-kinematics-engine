import struct

import pytest

from src.api.health import get_health_payload, set_health_metrics
from src.core.metrics import StreamMetrics
from src.core.pipeline import TelemetryPipeline
from src.telemetry.decoder import FRAME_HEADER, TelemetryDecoder


def test_pipeline_processes_valid_binary_frame() -> None:
    metrics = StreamMetrics()
    pipeline = TelemetryPipeline(metrics=metrics, enable_transforms=True, enable_estimation=True)

    payload = struct.pack(
        ">HHIIIihhh", FRAME_HEADER, 1, 1000, 230000000, 720000000, 150000, 10, -5, 0
    )
    crc = TelemetryDecoder.calculate_crc16(payload)
    raw_packet = payload + struct.pack(">H", crc)

    result = pipeline.process_binary_frame(raw_packet)

    assert result.success is True
    assert result.data is not None
    assert result.data.sequence_id == 1
    assert result.transformed is not None
    assert result.estimated is not None
    assert metrics.valid_frames_decoded == 1
    assert metrics.total_frames_received == 1


def test_pipeline_records_invalid_binary_frame_metrics() -> None:
    metrics = StreamMetrics()
    pipeline = TelemetryPipeline(metrics=metrics)

    raw_packet = b"\xaa\x55" + b"\x00" * 26

    result = pipeline.process_binary_frame(raw_packet)

    assert result.success is False
    assert metrics.total_frames_received == 1
    assert metrics.crc_errors == 1
    assert metrics.valid_frames_decoded == 0


def test_pipeline_processes_valid_nmea_sentence() -> None:
    metrics = StreamMetrics()
    pipeline = TelemetryPipeline(metrics=metrics, enable_transforms=True, enable_estimation=True)

    sentence = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"

    result = pipeline.process_nmea_sentence(sentence)

    assert result.success is True
    assert result.data is not None
    assert result.data.latitude_deg == pytest.approx(48.1173, abs=1e-4)
    assert result.transformed is not None
    assert result.estimated is not None
    assert metrics.valid_frames_decoded == 1
    assert metrics.total_frames_received == 1


def test_pipeline_records_invalid_nmea_metrics() -> None:
    metrics = StreamMetrics()
    pipeline = TelemetryPipeline(metrics=metrics)

    sentence = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*00"

    result = pipeline.process_nmea_sentence(sentence)

    assert result.success is False
    assert metrics.total_frames_received == 1
    assert metrics.valid_frames_decoded == 0


def test_pipeline_auto_detects_binary_and_nmea() -> None:
    metrics = StreamMetrics()
    pipeline = TelemetryPipeline(metrics=metrics)

    binary_payload = struct.pack(
        ">HHIIIihhh", FRAME_HEADER, 10, 2000, 230000000, 720000000, 150000, 10, -5, 0
    )
    binary_packet = binary_payload + struct.pack(">H", TelemetryDecoder.calculate_crc16(binary_payload))

    nmea_sentence = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"

    binary_result = pipeline.process(binary_packet)
    nmea_result = pipeline.process(nmea_sentence)

    assert binary_result.success is True
    assert nmea_result.success is True
    assert metrics.valid_frames_decoded == 2
    assert metrics.total_frames_received == 2


def test_pipeline_health_reflects_metrics() -> None:
    metrics = StreamMetrics()
    pipeline = TelemetryPipeline(metrics=metrics)
    set_health_metrics(metrics)

    binary_payload = struct.pack(
        ">HHIIIihhh", FRAME_HEADER, 1, 1000, 230000000, 720000000, 150000, 10, -5, 0
    )
    crc = TelemetryDecoder.calculate_crc16(binary_payload)
    raw_packet = binary_payload + struct.pack(">H", crc)

    pipeline.process_binary_frame(raw_packet)

    health = get_health_payload()
    assert health["metrics"]["valid_decoded"] == 1
    assert health["metrics"]["total_received"] == 1
    assert health["status"] == "healthy"


def test_pipeline_disable_transforms_and_estimation() -> None:
    metrics = StreamMetrics()
    pipeline = TelemetryPipeline(metrics=metrics, enable_transforms=False, enable_estimation=False)

    payload = struct.pack(
        ">HHIIIihhh", FRAME_HEADER, 1, 1000, 230000000, 720000000, 150000, 10, -5, 0
    )
    crc = TelemetryDecoder.calculate_crc16(payload)
    raw_packet = payload + struct.pack(">H", crc)

    result = pipeline.process_binary_frame(raw_packet)

    assert result.success is True
    assert result.transformed is None
    assert result.estimated is None


def test_pipeline_routes_nmea_bytes_to_parser() -> None:
    """Bytes starting with '$' must be routed to the NMEA parser, not the binary decoder."""
    metrics = StreamMetrics()
    pipeline = TelemetryPipeline(metrics=metrics)

    sentence = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
    result = pipeline.process(sentence.encode("ascii"))

    assert result.success is True
    assert result.data is not None
    assert metrics.valid_frames_decoded == 1
    assert metrics.total_frames_received == 1


def test_pipeline_routes_gprmc_bytes_to_parser() -> None:
    """GPRMC sentences delivered as bytes must reach the RMC parser."""
    metrics = StreamMetrics()
    pipeline = TelemetryPipeline(metrics=metrics)

    sentence = "$GPRMC,123519,A,4807.038,N,01131.000,E,022.0,180.0,010220,000.0,W*63"
    result = pipeline.process(sentence.encode("ascii"))

    assert result.success is True
    assert result.data is not None
    assert metrics.valid_frames_decoded == 1
    assert metrics.total_frames_received == 1


def test_pipeline_rejects_unsupported_nmea_bytes() -> None:
    """Unsupported NMEA sentences delivered as bytes must be recorded as errors."""
    metrics = StreamMetrics()
    pipeline = TelemetryPipeline(metrics=metrics)

    sentence = "$GPGSV,1,1,01,01,00,000,000*00"
    result = pipeline.process(sentence.encode("ascii"))

    assert result.success is False
    assert metrics.total_frames_received == 1
    assert metrics.valid_frames_decoded == 0


def test_pipeline_nmea_checksum_failure_via_bytes() -> None:
    """NMEA sentences with bad checksums delivered as bytes must increment crc_errors."""
    metrics = StreamMetrics()
    pipeline = TelemetryPipeline(metrics=metrics)

    sentence = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*00"
    result = pipeline.process(sentence.encode("ascii"))

    assert result.success is False
    assert metrics.total_frames_received == 1
    assert metrics.crc_errors == 1
    assert metrics.valid_frames_decoded == 0


def test_pipeline_nmea_metrics_shared_with_health() -> None:
    """NMEA frames processed via bytes must be reflected in the shared health metrics."""
    metrics = StreamMetrics()
    pipeline = TelemetryPipeline(metrics=metrics)
    set_health_metrics(metrics)

    sentence = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
    pipeline.process(sentence.encode("ascii"))

    health = get_health_payload()
    assert health["metrics"]["valid_decoded"] == 1
    assert health["metrics"]["total_received"] == 1
    assert health["status"] == "healthy"
