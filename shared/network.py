# Author: Lenard Felix

from __future__ import annotations

import json
import socket
from typing import cast

from shared.protocol import Message


def send_msg(sock: socket.socket, msg: Message) -> None:
    sock.sendall((json.dumps(msg) + "\n").encode())


def recv_line(buffer: str, sock: socket.socket) -> tuple[Message | None, str]:
    try:
        buffer += sock.recv(4096).decode()
    except BlockingIOError:
        pass
    if "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        raw = json.loads(line)
        if not isinstance(raw, dict):
            return None, buffer
        return cast(Message, raw), buffer
    return None, buffer
