# Author: Lenard Felix

from __future__ import annotations

import re
from typing import Iterable

from shared.models import Game, GamePhase, Player
from server.lib.player import active_players

MIN_BOARD_SIZE = 7
MAX_BOARD_SIZE = 15
VALID_BOARD_SIZES = frozenset(range(MIN_BOARD_SIZE, MAX_BOARD_SIZE + 1, 2))
MAX_JOINABLE_PLAYERS = 4
JOIN_CODE_PATTERN = re.compile(r"^[A-Z0-9]{4}$")

def is_valid_board_size(board_size: int) -> bool:
    return board_size in VALID_BOARD_SIZES


def normalize_join_code(code: str) -> str:
    return code.strip().upper()


def is_valid_join_code(code: str) -> bool:
    normalized = normalize_join_code(code)
    return bool(JOIN_CODE_PATTERN.fullmatch(normalized))


def can_join_game(game: Game, players: Iterable[Player]) -> bool:
    if game.game_phase != GamePhase.PREGAME:
        return False
    if not is_valid_board_size(game.board_size):
        return False
    if len(active_players(players)) >= MAX_JOINABLE_PLAYERS:
        return False
    return True
