# Author: Lenard Felix
 
from __future__ import annotations

from typing import Iterable

from shared.models import PlayerColor, PlayerData, PlayerStatus


def normalize_display_name(name: str) -> str:
    """Strip leading and trailing whitespace from a display name."""
    return name.strip()


def is_valid_display_name(name: str) -> bool:
    """Return ``True`` if the name is non-empty and at most 32 characters after normalisation."""
    normalized = normalize_display_name(name)
    return bool(normalized) and len(normalized) <= 32


def is_display_name_taken(players: Iterable[PlayerData], display_name: str) -> bool:
    """Return ``True`` if any player already has the given display name (case-insensitive)."""
    normalized = normalize_display_name(display_name).lower()

    for player in players:
        if normalize_display_name(player.display_name).lower() == normalized:
            return True

    return False


def next_join_order(players: Iterable[PlayerData]) -> int:
    """Return the next available join order (one above the current highest)."""
    highest = -1
    for player in players:
        if player.join_order > highest:
            highest = player.join_order
    return highest + 1


def active_players(players: Iterable[PlayerData]) -> list[PlayerData]:
    """Return only players who are still active participants in the round."""
    return [player for player in players if player.status == PlayerStatus.ACTIVE]


def session_players(players: Iterable[PlayerData]) -> list[PlayerData]:
    """Return players who are still present in the session, including spectators."""
    return [player for player in players if player.status != PlayerStatus.DEPARTED]


def next_available_color(players: Iterable[PlayerData]) -> PlayerColor | None:
    """Return the first unused player color in priority order, or ``None`` if all are taken."""
    used = {player.piece_color for player in session_players(players)}

    for color in (
        PlayerColor.RED,
        PlayerColor.YELLOW,
        PlayerColor.BLUE,
        PlayerColor.GREEN,
    ):
        if color not in used:
            return color

    return None
