# Author: Lenard Felix

import socket

from shared.network import recv_line, send_msg
from shared.protocol import Message


class ClientConnection:
    """Manages the connection to the server."""

    def __init__(self) -> None:
        self._sock: socket.socket | None = None
        self._buffer: str = ""

    def connect(self, host: str, port: int) -> bool:
        """Connect to the server. Returns True if successful."""
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(2)
            self._sock.connect((host, port))
            self._sock.setblocking(False)
            return True
        except OSError:
            self._sock = None
            return False

    def disconnect(self) -> None:
        """Disconnect from the server."""
        if self._sock:
            self._sock.close()
            self._sock = None

    def send(self, message: Message) -> None:
        """Send a message to the server."""
        if self._sock:
            send_msg(self._sock, message)

    def receive(self) -> Message | None:
        """Receive the next pending message from the server, or None if none available."""
        if not self._sock:
            return None
        try:
            msg, self._buffer = recv_line(self._buffer, self._sock)
            return msg
        except OSError:
            self._sock = None
            return None
