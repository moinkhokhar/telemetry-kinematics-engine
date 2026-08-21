import io
import json
from unittest.mock import MagicMock

from src.api.health import HealthRequestHandler, get_health_payload, metrics_collector


def test_health_payload_generation() -> None:
    metrics_collector.record_frame(sequence_id=0, is_valid=True)
    metrics_collector.record_frame(sequence_id=1, is_valid=True)

    payload = get_health_payload()
    assert payload["status"] == "healthy"
    assert payload["metrics"]["valid_decoded"] >= 2
    assert "loss_rate_pct" in payload["metrics"]


def test_health_request_handler_get() -> None:
    handler = HealthRequestHandler.__new__(HealthRequestHandler)
    handler.path = "/health"
    handler.wfile = io.BytesIO()
    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()

    handler.do_GET()

    handler.send_response.assert_called_once_with(200)
    handler.send_header.assert_any_call("Content-Type", "application/json")
    response_body = json.loads(handler.wfile.getvalue().decode("utf-8"))
    assert "status" in response_body
    assert "metrics" in response_body


def test_health_request_handler_404() -> None:
    handler = HealthRequestHandler.__new__(HealthRequestHandler)
    handler.path = "/unknown"
    handler.wfile = io.BytesIO()
    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()

    handler.do_GET()

    handler.send_response.assert_called_once_with(404)


def test_health_request_handler_log_message_suppression() -> None:
    handler = HealthRequestHandler.__new__(HealthRequestHandler)
    handler.log_message("%s - %s", "GET /health", "200")
