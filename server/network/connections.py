from __future__ import annotations

import socket
from threading import Lock

_connections: dict[str, socket.socket] = {}
_lock = Lock()


def register_connection(connection_id: str, conn: socket.socket) -> None:
    with _lock:
        _connections[connection_id] = conn


def unregister_connection(connection_id: str) -> None:
    with _lock:
        _connections.pop(connection_id, None)


def get_connection(connection_id: str) -> socket.socket | None:
    with _lock:
        return _connections.get(connection_id)
