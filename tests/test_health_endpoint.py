import io

from src.api.health import HealthRequestHandler, get_health_payload, metrics_collector


class MockSocket:
    def __init__(self) -> None:
        self.output = io.BytesIO()

    def makefile(self, *args, **kwargs) -> io.BytesIO:
        return self.output

    def sendall(self, data: bytes) -> None:
        self.output.write(data)


def test_health_payload_generation() -> None:
    metrics_collector.record_frame(sequence_id=0, is_valid=True)
    metrics_collector.record_frame(sequence_id=1, is_valid=True)

    payload = get_health_payload()
    assert payload["status"] == "healthy"
    assert payload["metrics"]["valid_decoded"] >= 2
    assert "loss_rate_pct" in payload["metrics"]


def test_health_request_handler_get() -> None:
    request = MockSocket()
    request.output.write(b"GET /health HTTP/1.1\r\nHost: localhost\r\n\r\n")
    request.output.seek(0)

    handler = HealthRequestHandler(request, ("127.0.0.1", 8080), None)  # type: ignore[arg-type]
    response = request.output.getvalue()
    assert b"200 OK" in response
    assert b"application/json" in response


def test_health_request_handler_404() -> None:
    request = MockSocket()
    request.output.write(b"GET /unknown HTTP/1.1\r\nHost: localhost\r\n\r\n")
    request.output.seek(0)

    handler = HealthRequestHandler(request, ("127.0.0.1", 8080), None)  # type: ignore[arg-type]
    response = request.output.getvalue()
    assert b"404" in response
