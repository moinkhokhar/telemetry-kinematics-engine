"""Application bootstrap for the telemetry kinematics engine."""

import os
import threading
from http.server import HTTPServer

from src.api.health import HealthRequestHandler, set_health_metrics
from src.core.logging import get_logger
from src.core.metrics import StreamMetrics
from src.core.pipeline import TelemetryPipeline
from src.ingestion.udp_server import UDPServer

logger = get_logger("application")


def create_pipeline() -> TelemetryPipeline:
    """Creates the telemetry pipeline with shared metrics."""
    metrics = StreamMetrics()
    pipeline = TelemetryPipeline(metrics=metrics)
    set_health_metrics(metrics)
    return pipeline


def run(pipeline: TelemetryPipeline) -> None:
    """Starts the UDP ingestion server and health HTTP server."""
    udp_server = UDPServer(
        host="0.0.0.0",
        port=int(os.getenv("TELEMETRY_PORT", "50051")),
        buffer_size=int(os.getenv("STREAM_BUFFER_SIZE", "65536")),
    )

    def handle_datagram(data: bytes) -> None:
        pipeline.process(data)

    def start_health_server() -> None:
        port = int(os.getenv("HEALTH_PORT", "8080"))
        server = HTTPServer(("0.0.0.0", port), HealthRequestHandler)
        logger.info("Health server listening on :%d", port)
        server.serve_forever()

    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    udp_server.start(handle_datagram)


def main() -> None:
    """Application entry point."""
    pipeline = create_pipeline()
    run(pipeline)


if __name__ == "__main__":
    main()
