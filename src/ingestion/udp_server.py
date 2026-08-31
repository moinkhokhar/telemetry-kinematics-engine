"""Synchronous UDP telemetry ingestion server."""

import socket
from typing import Callable, Optional

from src.core.logging import get_logger

logger = get_logger("udp_ingestion")


class UDPServer:
    """Simple synchronous UDP server for continuous telemetry ingestion."""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 50051,
        buffer_size: int = 65536,
    ) -> None:
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self._socket: Optional[socket.socket] = None

    def start(self, handler: Callable[[bytes], None]) -> None:
        """Starts the UDP server and invokes ``handler`` for each received datagram."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((self.host, self.port))
        logger.info("UDP server listening on %s:%d", self.host, self.port)
        try:
            while True:
                data, addr = self._socket.recvfrom(self.buffer_size)
                logger.debug("Received %d bytes from %s", len(data), addr)
                handler(data)
        except KeyboardInterrupt:
            logger.info("UDP server stopped")
        finally:
            self._socket.close()
            self._socket = None
