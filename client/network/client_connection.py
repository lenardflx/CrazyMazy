# Author: Lenard Felix

from __future__ import annotations

import socket
from typing import TYPE_CHECKING

from client.network.dispatch import dispatcher
from shared.events import Event, parse_event
from shared.lib.error import parse_error_payload
from shared.network import recv_line, send_msg
from shared.protocol import Message
from shared.schema import ErrorPayload

if TYPE_CHECKING:
    from client.network.state import ClientState


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

    @property
    def is_connected(self) -> bool:
        return self._sock is not None

    def _send_message(self, message: Message) -> None:
        """Send one message to the server."""
        if self._sock:
            send_msg(self._sock, message)

    def send_event(self, event: Event) -> bool:
        """Send one typed request event to the server."""
        try:
            self._send_message(event.to_message())
        except OSError:
            self._sock = None
            return False
        return True

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

    def receive_error(self) -> ErrorPayload | None:
        """Receive one error response if the next message is an error."""
        msg = self.receive()
        if msg is None or msg["type"] != "response.error":
            return None
        return parse_error_payload(msg["payload"])

    def poll(self, state: ClientState) -> None:
        """Consume one server response and dispatch its parsed event."""
        msg = self.receive()
        if msg is None:
            return
        event = parse_event(msg)
        if event is None:
            return
        dispatcher.dispatch(state, event)
