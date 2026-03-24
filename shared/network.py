# Author: Lenard Felix

from __future__ import annotations

import json
from typing import Protocol

from shared.protocol import Message, parse_message


class SupportsSendall(Protocol):
    def sendall(self, data: bytes | bytearray | memoryview, flags: int = 0, /) -> None: ...


class SupportsRecv(Protocol):
    def recv(self, bufsize: int, flags: int = 0, /) -> bytes: ...


def send_msg(sock: SupportsSendall, msg: Message) -> None:
    sock.sendall((json.dumps(msg) + "\n").encode())


def recv_line(buffer: str, sock: SupportsRecv) -> tuple[Message | None, str]:
    try:
        buffer += sock.recv(4096).decode()
    except BlockingIOError:
        pass
    if "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        raw = json.loads(line)
        return parse_message(raw), buffer
    return None, buffer
