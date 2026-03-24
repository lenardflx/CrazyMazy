# Author: Lenard Felix

from __future__ import annotations

from typing import Any, TypedDict

from shared.utils.ids import new_message_id


class EventType:
    # Client to Server
    CLIENT_ROOM_CREATE = "client.room.create"
    CLIENT_ROOM_JOIN = "client.room.join"
    CLIENT_ROOM_LEAVE = "client.room.leave"
    CLIENT_ROOM_START_GAME = "client.room.start_game"

    # Server to Client
    SERVER_SNAPSHOT = "server.snapshot"
    SERVER_RESPONSE_ERROR = "server.response.error"


class ErrorCode:
    INVALID_MESSAGE = "INVALID_MESSAGE"
    INVALID_PAYLOAD = "INVALID_PAYLOAD"

    ROOM_NOT_FOUND = "ROOM_NOT_FOUND"
    ROOM_FULL = "ROOM_FULL"


class Message(TypedDict, total=False):
    id: str
    type: str
    reply_to: str
    payload: dict[str, Any]


def make_message(msg_type: str, payload: dict[str, Any] | None = None) -> Message:
    return {
        "id": new_message_id(),
        "type": msg_type,
        "payload": payload or {},
    }


def get_message_type(msg: Message) -> str:
    value = msg.get("type")
    return value if isinstance(value, str) else ""
