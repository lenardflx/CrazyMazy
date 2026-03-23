# Author: Lenard Felix

import socket

from shared.network import recv_line, send_msg
from shared.protocol import EventType, Message


class ClientConnection:
    """Manages the connection to the server."""

    def __init__(self) -> None:
        """Initialize the client connection."""
        self._sock: socket.socket | None = None
        self._buffer: str = ""

    def connect(self, host: str, port: int) -> bool:
        """Connect to the server at the given host and port, including a handshake.
        Returns True if the connection was successful, False otherwise."""
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(2)
            self._sock.connect((host, port))
            if not self._healthcheck():
                self._sock.close()
                self._sock = None
                return False
            self._sock.setblocking(False)
            return True
        except OSError:
            self._sock = None
            return False

    def _healthcheck(self) -> bool:
        """Send a ping and verify the server responds with a pong."""
        assert self._sock is not None
        send_msg(self._sock, Message(type=EventType.CLIENT_HEALTH_PING).to_dict())
        msg, self._buffer = recv_line(self._buffer, self._sock)
        return bool(msg and msg.get("type") == EventType.SERVER_HEALTH_PONG)

    def disconnect(self) -> None:
        """Disconnect from the server."""
        if self._sock:
            self._sock.close()
            self._sock = None

    def send(self, message: dict) -> None:
        """Send a message to the server."""
        if self._sock:
            send_msg(self._sock, message)

    def receive(self) -> dict | None:
        """Receive a message from the server."""
        if not self._sock:
            return None
        try:
            msg, self._buffer = recv_line(self._buffer, self._sock)
            return msg
        except OSError:
            self._sock = None
            return None
