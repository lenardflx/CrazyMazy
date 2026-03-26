# Author: Lenard Felix

from __future__ import annotations

import json
import pytest

from shared.network import recv_line, send_msg
from shared.protocol import Message, make_message


class FakeSendSocket:
    def __init__(self) -> None:
        self.sent = b""

    def sendall(self, data: bytes | bytearray | memoryview, flags: int = 0) -> None:
        del flags
        self.sent += bytes(data)


class FakeRecvSocket:
    def __init__(self, chunks: list[bytes], *, raises_blocking: bool = False) -> None:
        self._chunks = list(chunks)
        self._raises_blocking = raises_blocking

    def recv(self, bufsize: int, flags: int = 0) -> bytes:
        del bufsize
        del flags
        if self._raises_blocking:
            raise BlockingIOError
        if not self._chunks:
            return b""
        return self._chunks.pop(0)


def test_send_msg_serializes_message_with_newline() -> None:
    sock = FakeSendSocket()
    msg = make_message("server.snapshot", {"ok": True})

    send_msg(sock, msg)

    assert sock.sent == (json.dumps(msg) + "\n").encode()


def test_send_msg_serializes_optional_message_fields() -> None:
    sock = FakeSendSocket()
    msg: Message = {
        "id": "msg_1",
        "type": "server.response.error",
        "reply_to": "msg_0",
        "payload": {"code": "INVALID_MESSAGE"},
    }

    send_msg(sock, msg)

    assert sock.sent == (json.dumps(msg) + "\n").encode()


def test_recv_line_waits_for_newline_before_parsing() -> None:
    full = json.dumps(make_message("server.snapshot"))
    midpoint = len(full) // 2
    sock = FakeRecvSocket([full[:midpoint].encode(), (full[midpoint:] + "\n").encode()])

    msg, buffer = recv_line("", sock)
    assert msg is None
    assert buffer == full[:midpoint]

    msg, buffer = recv_line(buffer, sock)
    assert msg == json.loads(full)
    assert buffer == ""


def test_recv_line_returns_message_and_preserves_remaining_buffer() -> None:
    first = json.dumps(make_message("server.snapshot"))
    second = json.dumps(make_message("server.response.error"))
    sock = FakeRecvSocket([(first + "\n" + second + "\n").encode()])

    msg, buffer = recv_line("", sock)

    assert msg is not None
    assert msg["type"] == "server.snapshot"
    assert buffer == second + "\n"


def test_recv_line_can_parse_prefilled_buffer_without_socket_data() -> None:
    first = json.dumps(make_message("server.snapshot"))
    second = json.dumps(make_message("server.response.error"))
    sock = FakeRecvSocket([])

    msg, buffer = recv_line(first + "\n" + second + "\n", sock)

    assert msg is not None
    assert msg["type"] == "server.snapshot"
    assert buffer == second + "\n"


def test_recv_line_raises_for_invalid_json() -> None:
    sock = FakeRecvSocket([b"{invalid json}\n"])

    with pytest.raises(json.JSONDecodeError):
        recv_line("", sock)


def test_recv_line_drops_non_dict_json_payload() -> None:
    sock = FakeRecvSocket([b'"hello"\n'])

    msg, buffer = recv_line("", sock)

    assert msg is None
    assert buffer == ""


def test_recv_line_drops_invalid_message_dict() -> None:
    sock = FakeRecvSocket([b'{"type":"server.snapshot","payload":{}}\n'])

    msg, buffer = recv_line("", sock)

    assert msg is None
    assert buffer == ""


def test_recv_line_keeps_buffer_when_socket_would_block() -> None:
    sock = FakeRecvSocket([], raises_blocking=True)

    msg, buffer = recv_line("partial", sock)

    assert msg is None
    assert buffer == "partial"
