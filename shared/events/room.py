# Author: Lenard Felix, Raphael Eiden

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Self

from shared.events.event import Event
from shared.lib.snapshot import parse_room_snapshot_payload
from shared.protocol import Message
from shared.schema import RoomSnapshotPayload


@dataclass(frozen=True)
class ClientJoinRoomEvent(Event):
    """Client request to join a room with a player name."""

    message_type = "client.room.join"

    room_id: str
    player_name: str

    def to_payload(self) -> Mapping[str, Any]:
        return {
            "room_id": self.room_id,
            "player_name": self.player_name,
        }

    @classmethod
    def from_message(cls, msg: Message) -> Self | None:
        room_id = msg["payload"].get("room_id")
        player_name = msg["payload"].get("player_name")
        if not isinstance(room_id, str) or not room_id.strip():
            return None
        if not isinstance(player_name, str) or not player_name.strip():
            return None

        return cls(
            message_id=msg["id"],
            room_id=room_id.strip(),
            player_name=player_name.strip(),
        )


@dataclass(frozen=True)
class ServerRoomSnapshotEvent(Event):
    """Server snapshot response for the current viewer."""

    message_type = "room.snapshot"

    payload: RoomSnapshotPayload

    def to_payload(self) -> Mapping[str, Any]:
        return self.payload

    @classmethod
    def from_message(cls, msg: Message) -> Self | None:
        payload = parse_room_snapshot_payload(msg["payload"])
        if payload is None:
            return None
        return cls(message_id=msg["id"], payload=payload)
