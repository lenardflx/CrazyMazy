from __future__ import annotations

MIN_BOARD_SIZE = 7
MAX_BOARD_SIZE = 15
VALID_BOARD_SIZES = frozenset(range(MIN_BOARD_SIZE, MAX_BOARD_SIZE + 1, 2))
MIN_STARTABLE_PLAYERS = 2
MAX_JOINABLE_PLAYERS = 4


def is_valid_board_size(board_size: int) -> bool:
    return board_size in VALID_BOARD_SIZES
