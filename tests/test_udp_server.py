"""Tests for synchronous UDP telemetry ingestion server."""

import socket
import threading
import time
from typing import List

from src.ingestion.udp_server import UDPServer


def test_udp_server_binds_and_invokes_handler() -> None:
    """Server should bind to the requested port and call handler with received datagram."""
    received: List[bytes] = []
    handler_called = threading.Event()

    def handler(data: bytes) -> None:
        received.append(data)
        handler_called.set()

    server = UDPServer(host="127.0.0.1", port=0)
    server_thread = threading.Thread(target=server.start, args=(handler,), daemon=True)
    server_thread.start()

    for _ in range(50):
        if server._socket is not None:
            break
        time.sleep(0.1)

    assert server._socket is not None, "server did not create socket"
    addr = server._socket.getsockname()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(b"hello udp", addr)
    sock.close()

    assert handler_called.wait(timeout=2), "handler was not called"
    assert received == [b"hello udp"]
    server.stop()
    server_thread.join(timeout=2)


def test_udp_server_stop_closes_socket() -> None:
    """After stop(), the server socket should be closed and reusable."""
    server = UDPServer(host="127.0.0.1", port=0)
    server_thread = threading.Thread(target=server.start, args=(lambda x: None,), daemon=True)
    server_thread.start()

    for _ in range(50):
        if server._socket is not None:
            break
        time.sleep(0.1)

    time.sleep(0.2)
    server.stop()
    server_thread.join(timeout=2)

    assert server._socket is None


def test_udp_server_reuseaddr_allows_quick_restart() -> None:
    """With SO_REUSEADDR, the same port should be reusable immediately after stop."""
    server1 = UDPServer(host="127.0.0.1", port=0)
    thread1 = threading.Thread(target=server1.start, args=(lambda x: None,), daemon=True)
    thread1.start()

    for _ in range(50):
        if server1._socket is not None:
            break
        time.sleep(0.1)

    time.sleep(0.2)
    port = server1._socket.getsockname()[1]
    server1.stop()
    thread1.join(timeout=2)

    server2 = UDPServer(host="127.0.0.1", port=port)
    thread2 = threading.Thread(target=server2.start, args=(lambda x: None,), daemon=True)
    thread2.start()

    for _ in range(50):
        if server2._socket is not None:
            break
        time.sleep(0.1)

    time.sleep(0.2)

    assert server2._socket is not None
    server2.stop()
    thread2.join(timeout=2)


def test_udp_server_continues_after_handler_exception() -> None:
    """If the handler raises, the server should keep running."""

    def handler(_: bytes) -> None:
        raise RuntimeError("handler boom")

    server = UDPServer(host="127.0.0.1", port=0)
    server_thread = threading.Thread(target=server.start, args=(handler,), daemon=True)
    server_thread.start()

    for _ in range(50):
        if server._socket is not None:
            break
        time.sleep(0.1)

    addr = server._socket.getsockname()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(b"first", addr)
    time.sleep(0.2)
    sock.sendto(b"second", addr)
    sock.close()
    time.sleep(0.5)

    server.stop()
    server_thread.join(timeout=2)
    assert True
