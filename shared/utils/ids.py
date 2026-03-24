# Author: Lenard Felix

from __future__ import annotations

from uuid import uuid4


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def new_message_id() -> str:
    return _new_id("msg")


def new_room_id() -> str:
    return _new_id("room")


def new_member_id() -> str:
    return _new_id("member")


def new_match_id() -> str:
    return _new_id("match")


def new_connection_id() -> str:
    return _new_id("conn")