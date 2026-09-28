"""Application bootstrap for the telemetry kinematics engine."""

import os
import signal
import threading
from dataclasses import dataclass
from http.server import HTTPServer
from typing import Any, Optional

from src.api.health import HealthRequestHandler, set_health_metrics
from src.core.logging import get_logger
from src.core.metrics import StreamMetrics
from src.core.pipeline import TelemetryPipeline
from src.ingestion.udp_server import UDPServer

logger = get_logger("application")


@dataclass(frozen=True)
class AppConfig:
    """Strongly typed application configuration."""

    telemetry_host: str = "0.0.0.0"
    telemetry_port: int = 50051
    stream_buffer_size: int = 65536
    health_host: str = "0.0.0.0"
    health_port: int = 8080

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Builds config from environment variables with validation."""
        telemetry_port = int(os.getenv("TELEMETRY_PORT", str(cls.telemetry_port)))
        if not (1 <= telemetry_port <= 65535):
            raise ValueError(f"TELEMETRY_PORT must be between 1 and 65535, got {telemetry_port}")
        health_port = int(os.getenv("HEALTH_PORT", str(cls.health_port)))
        if not (1 <= health_port <= 65535):
            raise ValueError(f"HEALTH_PORT must be between 1 and 65535, got {health_port}")
        buffer_size = int(os.getenv("STREAM_BUFFER_SIZE", str(cls.stream_buffer_size)))
        if buffer_size <= 0:
            raise ValueError(f"STREAM_BUFFER_SIZE must be positive, got {buffer_size}")
        return cls(
            telemetry_host=os.getenv("TELEMETRY_HOST", cls.telemetry_host),
            telemetry_port=telemetry_port,
            stream_buffer_size=buffer_size,
            health_host=os.getenv("HEALTH_HOST", cls.health_host),
            health_port=health_port,
        )


def create_pipeline() -> TelemetryPipeline:
    """Creates the telemetry pipeline with shared metrics."""
    metrics = StreamMetrics()
    pipeline = TelemetryPipeline(metrics=metrics)
    set_health_metrics(metrics)
    return pipeline


def run(pipeline: TelemetryPipeline, config: Optional[AppConfig] = None) -> None:
    """Starts the UDP ingestion server and health HTTP server."""
    if config is None:
        config = AppConfig.from_env()

    udp_server = UDPServer(
        host=config.telemetry_host,
        port=config.telemetry_port,
        buffer_size=config.stream_buffer_size,
    )

    health_server = HTTPServer((config.health_host, config.health_port), HealthRequestHandler)
    health_thread = threading.Thread(target=health_server.serve_forever, daemon=True)
    health_thread.start()
    logger.info("Health server listening on %s:%d", config.health_host, config.health_port)

    def _shutdown(signum: int, _: Any) -> None:
        logger.info("Received signal %s, shutting down", signum)
        udp_server.stop()
        health_server.shutdown()

    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGTERM, _shutdown)
        signal.signal(signal.SIGINT, _shutdown)
    else:
        logger.warning("Skipping signal registration: not running in main thread")

    def handle_datagram(data: bytes) -> None:
        try:
            pipeline.process(data)
        except Exception as exc:  # pragma: no cover - defensive logging path
            logger.error("Unhandled error processing telemetry datagram: %s", exc)

    udp_server.start(handle_datagram)


def main() -> None:
    """Application entry point."""
    config = AppConfig.from_env()
    pipeline = create_pipeline()
    run(pipeline, config)


if __name__ == "__main__":
    main()
