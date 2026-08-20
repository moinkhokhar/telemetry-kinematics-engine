import json
import logging

from src.core.exceptions import (
    ChecksumMismatchError,
    CoordinateOutOfBoundsError,
    FilterDivergenceError,
    FrameLengthError,
    InvalidPacketHeaderError,
    TelemetryEngineError,
)
from src.core.logging import JSONFormatter, get_logger
from src.core.metrics import StreamMetrics


def test_exception_inheritance():
    assert issubclass(ChecksumMismatchError, TelemetryEngineError)
    assert issubclass(InvalidPacketHeaderError, TelemetryEngineError)
    assert issubclass(FrameLengthError, TelemetryEngineError)
    assert issubclass(FilterDivergenceError, TelemetryEngineError)
    assert issubclass(CoordinateOutOfBoundsError, TelemetryEngineError)


def test_json_logging_output():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Telemetry packet received",
        args=(),
        exc_info=None,
    )
    output = formatter.format(record)
    parsed = json.loads(output)
    assert parsed["level"] == "INFO"
    assert parsed["message"] == "Telemetry packet received"
    assert "timestamp" in parsed


def test_get_logger_instance():
    logger = get_logger("unit_test_pipeline")
    assert logger.name == "unit_test_pipeline"
    assert len(logger.handlers) >= 1


def test_stream_metrics_tracking():
    metrics = StreamMetrics()
    metrics.record_frame(sequence_id=0, is_valid=True)
    metrics.record_frame(sequence_id=1, is_valid=True)
    # Frame 2 dropped
    metrics.record_frame(sequence_id=3, is_valid=True)
    metrics.record_frame(sequence_id=4, is_valid=False, error_type="crc")

    summary = metrics.health_summary
    assert summary["valid_decoded"] == 3
    assert summary["dropped"] == 1
    assert summary["crc_errors"] == 1
    assert metrics.packet_loss_rate == 25.0
