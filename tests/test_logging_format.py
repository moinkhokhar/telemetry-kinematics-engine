import json
import logging

import pytest

from src.core.logging import JSONFormatter, configure_logging, get_logger


def test_json_logging_structure() -> None:
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_service",
        level=logging.WARNING,
        pathname=__file__,
        lineno=42,
        msg="GPS signal degraded",
        args=(),
        exc_info=None,
    )
    output = formatter.format(record)
    parsed = json.loads(output)

    assert parsed["level"] == "WARNING"
    assert parsed["logger"] == "test_service"
    assert parsed["message"] == "GPS signal degraded"
    assert "timestamp" in parsed


def test_log_level_environment_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    configure_logging()
    logger = get_logger("debug_test")
    assert logger.getEffectiveLevel() == logging.DEBUG
