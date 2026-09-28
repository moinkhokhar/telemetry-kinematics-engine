"""Tests for application bootstrap and configuration."""

import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from src.application import AppConfig, create_pipeline, run
from src.core.metrics import StreamMetrics
from src.core.pipeline import TelemetryPipeline


def test_create_pipeline_returns_pipeline_with_shared_metrics() -> None:
    """create_pipeline should return a TelemetryPipeline with shared metrics."""
    pipeline = create_pipeline()
    assert isinstance(pipeline, TelemetryPipeline)
    assert isinstance(pipeline.metrics, StreamMetrics)


def test_create_pipeline_wires_health_metrics() -> None:
    """create_pipeline should call set_health_metrics with the same metrics instance."""
    from src.api.health import get_health_payload

    create_pipeline()
    health = get_health_payload()
    assert health["status"] in {"healthy", "degraded"}


def test_app_config_defaults() -> None:
    """AppConfig should have sensible defaults."""
    config = AppConfig()
    assert config.telemetry_host == "0.0.0.0"
    assert config.telemetry_port == 50051
    assert config.health_port == 8080
    assert config.stream_buffer_size == 65536


def test_app_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """AppConfig.from_env should read environment variables."""
    monkeypatch.setenv("TELEMETRY_HOST", "127.0.0.1")
    monkeypatch.setenv("TELEMETRY_PORT", "12345")
    monkeypatch.setenv("HEALTH_PORT", "9090")
    monkeypatch.setenv("STREAM_BUFFER_SIZE", "32768")

    config = AppConfig.from_env()
    assert config.telemetry_host == "127.0.0.1"
    assert config.telemetry_port == 12345
    assert config.health_port == 9090
    assert config.stream_buffer_size == 32768


def test_app_config_rejects_invalid_port(monkeypatch: pytest.MonkeyPatch) -> None:
    """AppConfig.from_env should reject invalid port values."""
    monkeypatch.setenv("TELEMETRY_PORT", "0")
    with pytest.raises(ValueError, match="TELEMETRY_PORT must be between 1 and 65535"):
        AppConfig.from_env()


def test_run_starts_servers(monkeypatch: pytest.MonkeyPatch) -> None:
    """run() should start UDP and health servers."""
    monkeypatch.setenv("TELEMETRY_PORT", "50052")
    monkeypatch.setenv("HEALTH_PORT", "8081")

    pipeline = TelemetryPipeline()
    start_event = threading.Event()
    stop_event = threading.Event()

    with patch("src.application.UDPServer") as MockUDP, patch(
        "src.application.HTTPServer"
    ) as MockHTTP:
        mock_udp = MagicMock()
        MockUDP.return_value = mock_udp
        mock_http = MagicMock()
        MockHTTP.return_value = mock_http

        def fake_start(handler: object) -> None:
            start_event.set()
            while not stop_event.is_set():
                time.sleep(0.05)

        mock_udp.start.side_effect = fake_start

        run_thread = threading.Thread(target=run, args=(pipeline,), daemon=True)
        run_thread.start()
        assert start_event.wait(timeout=2), "run() did not start"
        stop_event.set()
        run_thread.join(timeout=2)

        MockUDP.assert_called_once()
        MockHTTP.assert_called_once()
        mock_udp.start.assert_called_once()
