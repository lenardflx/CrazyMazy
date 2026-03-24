from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Self

from shared.protocol import Message


@dataclass(frozen=True)
class Event(ABC):
    message_type: ClassVar[str]
    message_id: str

    @classmethod
    @abstractmethod
    def from_message(cls, msg: Message) -> Self | None:
        raise NotImplementedError


@dataclass(frozen=True)
class ClientJoinRoomEvent(Event):
    message_type = "client.room.join"

    room_id: str
    player_name: str

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
