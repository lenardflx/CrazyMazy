from __future__ import annotations

import socket
from typing import cast

from client.network.client_connection import ClientConnection
import client.network.handlers
from client.network.state import ClientState
from shared.events import ClientJoinRoomEvent


class FakeSocket:
    def __init__(self) -> None:
        self.sent = b""

    def sendall(self, data: bytes | bytearray | memoryview, flags: int = 0, /) -> None:
        del flags
        self.sent += bytes(data)


def make_message_bytes(raw: str) -> bytes:
    return raw.encode()


class FakeRecvSocket(FakeSocket):
    def __init__(self, chunks: list[bytes]) -> None:
        super().__init__()
        self._chunks = list(chunks)

    def recv(self, bufsize: int, flags: int = 0, /) -> bytes:
        del bufsize
        del flags
        if not self._chunks:
            return b""
        return self._chunks.pop(0)


def test_send_event_serializes_event_to_socket() -> None:
    conn = ClientConnection()
    fake_sock = FakeSocket()
    conn._sock = cast(socket.socket, fake_sock)

    conn.send_event(
        ClientJoinRoomEvent(
            room_id="ROOM-1",
            player_name="Ada",
        )
    )

    sent = fake_sock.sent.decode()
    assert '"type": "client.room.join"' in sent
    assert '"room_id": "ROOM-1"' in sent
    assert '"player_name": "Ada"' in sent


def test_poll_updates_snapshot_state_from_server_message() -> None:
    conn = ClientConnection()
    conn._sock = cast(
        socket.socket,
        FakeRecvSocket([make_message_bytes('{"id":"msg_1","type":"room.snapshot","payload":{"room_id":"ROOM-1","joined":true}}\n')]),
    )
    state = ClientState()

    conn.poll(state)

    assert state.last_error is None


def test_poll_updates_error_state_from_server_message() -> None:
    conn = ClientConnection()
    conn._sock = cast(
        socket.socket,
        FakeRecvSocket([make_message_bytes('{"id":"msg_1","type":"response.error","payload":{"code":"ROOM_NOT_FOUND","message":"missing"}}\n')]),
    )
    state = ClientState()

    conn.poll(state)

    assert state.last_error == {"code": "ROOM_NOT_FOUND", "message": "missing"}
