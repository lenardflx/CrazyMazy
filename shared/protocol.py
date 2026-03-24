# Author: Lenard Felix

from __future__ import annotations

from typing import Any, NotRequired, TypedDict, cast

from shared.utils.ids import new_message_id


class ErrorCode:
    INVALID_MESSAGE = "INVALID_MESSAGE"
    INVALID_PAYLOAD = "INVALID_PAYLOAD"

    ROOM_NOT_FOUND = "ROOM_NOT_FOUND"
    ROOM_FULL = "ROOM_FULL"


class Message(TypedDict):
    id: str
    type: str
    payload: dict[str, Any]
    reply_to: NotRequired[str]


def make_message(msg_type: str, payload: dict[str, Any] | None = None) -> Message:
    return {
        "id": new_message_id(),
        "type": msg_type,
        "payload": payload or {},
    }


def parse_message(raw: object) -> Message | None:
    if not isinstance(raw, dict):
        return None
    if not (
        isinstance(raw.get("id"), str)
        and isinstance(raw.get("type"), str)
        and isinstance(raw.get("payload"), dict)
    ):
        return None
    if "reply_to" in raw and not isinstance(raw["reply_to"], str):
        return None
    return cast(Message, raw)
