# Author: Lenard Felix, Raphael Eiden

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Self

from shared.events.event import Event
from shared.lib.game import (
    parse_client_game_add_npc_payload,
    parse_client_game_move_player_payload,
    parse_client_game_shift_tile_payload,
    parse_server_game_left_payload,
)
from shared.lib.parse import parse_int, parse_str
from shared.lib.snapshot import parse_game_snapshot_payload
from shared.protocol import Message
from shared.types.enums import NpcDifficulty
from shared.types.payloads import (
    ClientCreateLobbyPayload,
    ClientGameAddNpcPayload,
    ClientJoinGamePayload,
    GameSnapshotPayload,
    ServerGameLeftPayload,
)

@dataclass(frozen=True)
class ClientCreateLobbyEvent(Event):
    message_type = "client.game.create_lobby"

    board_size: int
    player_name: str

    def to_payload(self) -> Mapping[str, Any]:
        payload: ClientCreateLobbyPayload = {
            "board_size": self.board_size,
            "player_name": self.player_name,
        }
        return payload

    @classmethod
    def from_message(cls, msg: Message) -> Self | None:
        board_size = parse_int(msg["payload"].get("board_size"))
        player_name = parse_str(msg["payload"].get("player_name"))
        if board_size is None or player_name is None or not player_name.strip():
            return None
        return cls(
            message_id=msg["id"],
            board_size=board_size,
            player_name=player_name.strip(),
        )


@dataclass(frozen=True)
class ClientJoinGameEvent(Event):
    """
    This event is fired by the client when a player has typed in their display name
    and an invitation code and now wants to join a game. When received, the server checks
    whether the game actually exists
    """
    message_type = "client.game.join"

    join_code: str
    player_name: str

    def to_payload(self) -> Mapping[str, Any]:
        payload: ClientJoinGamePayload = {
            "join_code": self.join_code,
            "player_name": self.player_name,
        }
        return payload

    @classmethod
    def from_message(cls, msg: Message) -> Self | None:
        join_code = parse_str(msg["payload"].get("join_code"))
        player_name = parse_str(msg["payload"].get("player_name"))
        if join_code is None or not join_code.strip() or player_name is None or not player_name.strip():
            return None
        return cls(
            message_id=msg["id"],
            join_code=join_code.strip(),
            player_name=player_name.strip(),
        )


@dataclass(frozen=True)
class ServerGameSnapshotEvent(Event):
    message_type = "game.snapshot"

    payload: GameSnapshotPayload

    def to_payload(self) -> Mapping[str, Any]:
        return self.payload

    @classmethod
    def from_message(cls, msg: Message) -> Self | None:
        payload = parse_game_snapshot_payload(msg["payload"])
        if payload is None:
            return None
        return cls(message_id=msg["id"], payload=payload)


@dataclass(frozen=True)
class ClientGameStartEvent(Event):
    message_type = "client.game.start"

    def to_payload(self) -> Mapping[str, Any]:
        return {}

    @classmethod
    def from_message(cls, msg: Message) -> Self | None:
        if msg["payload"]:
            return None
        return cls(message_id=msg["id"])


@dataclass(frozen=True)
class ClientGameAddNpcEvent(Event):
    message_type = "client.game.add_npc"

    difficulty: NpcDifficulty

    def to_payload(self) -> Mapping[str, Any]:
        payload: ClientGameAddNpcPayload = {"difficulty": self.difficulty}
        return payload

    @classmethod
    def from_message(cls, msg: Message) -> Self | None:
        payload = parse_client_game_add_npc_payload(msg["payload"])
        if payload is None:
            return None
        return cls(message_id=msg["id"], difficulty=NpcDifficulty(payload["difficulty"]))


@dataclass(frozen=True)
class ClientGameShiftTileEvent(Event):
    message_type = "client.game.shift_tile"

    insertion_side: str
    insertion_index: int
    rotation: int

    def to_payload(self) -> Mapping[str, Any]:
        return {
            "insertion_side": self.insertion_side,
            "insertion_index": self.insertion_index,
            "rotation": self.rotation,
        }

    @classmethod
    def from_message(cls, msg: Message) -> Self | None:
        payload = parse_client_game_shift_tile_payload(msg["payload"])
        if payload is None:
            return None
        return cls(message_id=msg["id"], **payload)


@dataclass(frozen=True)
class ClientGameMovePlayerEvent(Event):
    message_type = "client.game.move_player"

    x: int
    y: int

    def to_payload(self) -> Mapping[str, Any]:
        return {"x": self.x, "y": self.y}

    @classmethod
    def from_message(cls, msg: Message) -> Self | None:
        payload = parse_client_game_move_player_payload(msg["payload"])
        if payload is None:
            return None
        return cls(message_id=msg["id"], **payload)


@dataclass(frozen=True)
class ClientGameEndTurnEvent(Event):
    message_type = "client.game.end_turn"

    def to_payload(self) -> Mapping[str, Any]:
        return {}

    @classmethod
    def from_message(cls, msg: Message) -> Self | None:
        if msg["payload"]:
            return None
        return cls(message_id=msg["id"])


@dataclass(frozen=True)
class ClientGameLeaveEvent(Event):
    message_type = "client.game.leave"

    def to_payload(self) -> Mapping[str, Any]:
        return {}

    @classmethod
    def from_message(cls, msg: Message) -> Self | None:
        if msg["payload"]:
            return None
        return cls(message_id=msg["id"])


@dataclass(frozen=True)
class ClientGameGiveUpEvent(Event):
    message_type = "client.game.give_up"

    def to_payload(self) -> Mapping[str, Any]:
        return {}

    @classmethod
    def from_message(cls, msg: Message) -> Self | None:
        if msg["payload"]:
            return None
        return cls(message_id=msg["id"])


@dataclass(frozen=True)
class ServerGameLeftEvent(Event):
    # sent to the player who left, redundant staged for removal!!
    message_type = "server.game.left"

    payload: ServerGameLeftPayload

    def to_payload(self) -> Mapping[str, Any]:
        return self.payload

    @classmethod
    def from_message(cls, msg: Message) -> Self | None:
        payload = parse_server_game_left_payload(msg["payload"])
        if payload is None:
            return None
        return cls(message_id=msg["id"], payload=payload)
