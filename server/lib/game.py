# Author: Lenard Felix

from __future__ import annotations

import re
from typing import Iterable

from shared.lib.lobby import MAX_JOINABLE_PLAYERS, VALID_BOARD_SIZES, is_valid_board_size
from shared.models import GameData, GamePhase, PlayerData
from server.lib.player import active_players
JOIN_CODE_PATTERN = re.compile(r"^[A-Z0-9]{4}$")


def normalize_join_code(code: str) -> str:
    return code.strip().upper()


def is_valid_join_code(code: str) -> bool:
    normalized = normalize_join_code(code)
    return bool(JOIN_CODE_PATTERN.fullmatch(normalized))


def can_join_game(game: GameData, players: Iterable[PlayerData]) -> bool:
    if game.game_phase != GamePhase.PREGAME:
        return False
    if not is_valid_board_size(game.board_size):
        return False
    if len(active_players(players)) >= MAX_JOINABLE_PLAYERS:
        return False
    return True
