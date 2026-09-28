"""Lightweight HTTP server exposing real-time stream health telemetry."""

import json
from http.server import BaseHTTPRequestHandler
from typing import Any

from src.core.metrics import StreamMetrics

_health_metrics: StreamMetrics | None = None


def set_health_metrics(metrics: StreamMetrics) -> None:
    """Shares the runtime metrics instance with the health endpoint."""
    global _health_metrics
    _health_metrics = metrics


def get_health_payload() -> dict[str, Any]:
    """Generates structured health dictionary."""
    if _health_metrics is None:
        return {
            "status": "degraded",
            "metrics": {
                "total_received": 0,
                "valid_decoded": 0,
                "dropped": 0,
                "crc_errors": 0,
                "invalid_headers": 0,
                "loss_rate_pct": 0.0,
            },
        }
    metrics = _health_metrics
    return {
        "status": "healthy" if metrics.packet_loss_rate < 5.0 else "degraded",
        "metrics": metrics.health_summary,
    }


class HealthRequestHandler(BaseHTTPRequestHandler):
    """Handles health and readiness probe requests."""

    def do_GET(self) -> None:
        if self.path == "/health":
            payload = get_health_payload()
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        pass
