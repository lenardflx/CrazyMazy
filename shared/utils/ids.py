# Author: Lenard Felix, Raphael Eiden
"""
This file is used to generate unique identifiers for
messages, game lobbies, etc.

Each identifier consists of a prefix and a UUID4 string
of 12 characters.
"""

from __future__ import annotations

from uuid import uuid4


def _new_id(prefix: str) -> str:
    """
    Generate a unique identifier based on UUID4.

    :param prefix:
    :return:
    """
    return f"{prefix}_{uuid4().hex[:12]}"


def new_message_id() -> str:
    return _new_id("msg")


def new_game_id() -> str:
    return _new_id("game")


def new_member_id() -> str:
    return _new_id("member")


def new_connection_id() -> str:
    return _new_id("conn")