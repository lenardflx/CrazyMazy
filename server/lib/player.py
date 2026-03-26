# Author: Lenard Felix
 
from __future__ import annotations

from typing import Iterable

from shared.models import PlayerColor, PlayerData, PlayerStatus


def normalize_display_name(name: str) -> str:
    return name.strip()


def is_valid_display_name(name: str) -> bool:
    normalized = normalize_display_name(name)
    return bool(normalized) and len(normalized) <= 32


def is_display_name_taken(players: Iterable[PlayerData], display_name: str) -> bool:
    normalized = normalize_display_name(display_name).lower()

    for player in players:
        if normalize_display_name(player.display_name).lower() == normalized:
            return True

    return False


def next_join_order(players: Iterable[PlayerData]) -> int:
    highest = -1
    for player in players:
        if player.join_order > highest:
            highest = player.join_order
    return highest + 1


def active_players(players: Iterable[PlayerData]) -> list[PlayerData]:
    return [player for player in players if player.status != PlayerStatus.DEPARTED]


def next_available_color(players: Iterable[PlayerData]) -> PlayerColor | None:
    used = {player.piece_color for player in active_players(players)}

    # TODO: is this a good way to assign colors? Should we rethink the color model
    for color in (
        PlayerColor.RED,
        PlayerColor.YELLOW,
        PlayerColor.BLUE,
        PlayerColor.GREEN,
    ):
        if color not in used:
            return color

    return None
