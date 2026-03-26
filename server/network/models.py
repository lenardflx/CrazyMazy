# Author: Lenard Felix

from __future__ import annotations

from dataclasses import dataclass
import socket

from shared.protocol import Message


@dataclass(frozen=True)
class RequestContext:
    conn: socket.socket
    addr: tuple[str, int]
    connection_id: str


@dataclass(frozen=True)
class OutgoingMessage:
    conn: socket.socket
    msg: Message
