# Author: Lenard Felix, Raphael Eiden

from __future__ import annotations

MIN_BOARD_SIZE = 7
MAX_BOARD_SIZE = 15
VALID_BOARD_SIZES = frozenset(range(MIN_BOARD_SIZE, MAX_BOARD_SIZE + 1, 2))
VALID_INSERT_TIMEOUTS = frozenset([5, 10, 20, 30, 60, 90, 120])
VALID_MOVE_TIMEOUTS = frozenset([5, 10, 20, 30, 60, 90, 120])
MIN_STARTABLE_PLAYERS = 2
MAX_JOINABLE_PLAYERS = 4


def is_valid_board_size(board_size: int) -> bool:
    """Return ``True`` if ``board_size`` is an odd value within the allowed range."""
    return board_size in VALID_BOARD_SIZES
