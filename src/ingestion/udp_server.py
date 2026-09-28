"""Synchronous UDP telemetry ingestion server."""

import socket
import threading
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
        self._stop_event = threading.Event()

    def start(self, handler: Callable[[bytes], None]) -> None:
        """Starts the UDP server and invokes ``handler`` for each received datagram."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.host, self.port))
        self._socket.setblocking(True)
        logger.info("UDP server listening on %s:%d", self.host, self.port)
        try:
            while not self._stop_event.is_set():
                try:
                    data, addr = self._socket.recvfrom(self.buffer_size)
                except OSError:
                    if self._stop_event.is_set():
                        break
                    raise
                logger.debug("Received %d bytes from %s", len(data), addr)
                handler(data)
        except KeyboardInterrupt:
            logger.info("UDP server stopped")
        finally:
            self.stop()

    def stop(self) -> None:
        """Signals the server loop to exit and closes the socket."""
        self._stop_event.set()
        if self._socket is not None:
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None
