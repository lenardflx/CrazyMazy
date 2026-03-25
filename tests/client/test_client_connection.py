from __future__ import annotations

import json
import socket
from typing import cast

from client.network.client_connection import ClientConnection
import client.network.handlers
from client.network.state import ClientState
from shared.events import ClientJoinGameEvent


class FakeSocket:
    def __init__(self) -> None:
        self.sent = b""

    def sendall(self, data: bytes | bytearray | memoryview, flags: int = 0, /) -> None:
        del flags
        self.sent += bytes(data)


def make_message_bytes(raw: str) -> bytes:
    return raw.encode()


def make_snapshot_message_bytes() -> bytes:
    return make_message_bytes(
        json.dumps(
            {
                "id": "msg_1",
                "type": "game.snapshot",
                "payload": {
                    "game_id": "550e8400-e29b-41d4-a716-446655440000",
                    "code": "GAME-1",
                    "phase": "GAME",
                    "revision": 7,
                    "board_size": 7,
                    "leader_player_id": "550e8400-e29b-41d4-a716-446655440001",
                    "turn": {
                        "current_player_id": "550e8400-e29b-41d4-a716-446655440001",
                        "turn_phase": "MOVE",
                        "blocked_insertion_side": "LEFT",
                        "blocked_insertion_index": 3,
                    },
                    "tiles": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440010",
                            "row": 0,
                            "column": 0,
                            "tile_type": "CORNER",
                            "rotation": 1,
                            "is_spare": False,
                            "treasure_type": "BOOK",
                        },
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440011",
                            "tile_type": "T",
                            "rotation": 2,
                            "is_spare": True,
                            "treasure_type": None,
                        },
                    ],
                    "players": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440001",
                            "display_name": "Ada",
                            "status": "ACTIVE",
                            "result": "NONE",
                            "placement": None,
                            "join_order": 0,
                            "piece_color": "RED",
                            "position": {"x": 1, "y": 2},
                            "collected_treasures": ["BOOK"],
                            "remaining_treasure_count": 1,
                        }
                    ],
                    "viewer": {
                        "player_id": "550e8400-e29b-41d4-a716-446655440001",
                        "is_leader": True,
                        "is_current_player": True,
                        "active_treasure_type": "OWL",
                        "collected_treasures": ["BOOK"],
                        "remaining_treasure_count": 1,
                    },
                },
            }
        )
        + "\n"
    )


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
        ClientJoinGameEvent(
            join_code="GAME",
            player_name="Ada",
        )
    )

    sent = fake_sock.sent.decode()
    assert '"type": "client.game.join"' in sent
    assert '"join_code": "GAME"' in sent
    assert '"player_name": "Ada"' in sent


def test_poll_updates_snapshot_state_from_server_message() -> None:
    conn = ClientConnection()
    conn._sock = cast(
        socket.socket,
        FakeRecvSocket(
            [
                make_snapshot_message_bytes()
            ]
        ),
    )
    state = ClientState()

    conn.poll(state)

    assert state.last_error is None
    assert state.game_snapshot is not None
    assert state.game_snapshot["viewer"] is not None
    assert state.game_snapshot["viewer"]["active_treasure_type"] == "OWL"
    assert state.game_snapshot["players"][0]["collected_treasures"] == ["BOOK"]


def test_poll_updates_error_state_from_server_message() -> None:
    conn = ClientConnection()
    conn._sock = cast(
        socket.socket,
        FakeRecvSocket([make_message_bytes('{"id":"msg_1","type":"response.error","payload":{"code":"GAME_NOT_FOUND","message":"missing"}}\n')]),
    )
    state = ClientState()

    conn.poll(state)

    assert state.last_error == {"code": "GAME_NOT_FOUND", "message": "missing"}
