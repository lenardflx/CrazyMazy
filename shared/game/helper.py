from __future__ import annotations

from random import shuffle

from shared.game.board import Position
from shared.types.enums import PlayerColor, TreasureType


def start_position_for_color(board_size: int, color: PlayerColor) -> Position:
    return {
        PlayerColor.RED: (0, 0),
        PlayerColor.BLUE: (board_size - 1, 0),
        PlayerColor.GREEN: (0, board_size - 1),
        PlayerColor.YELLOW: (board_size - 1, board_size - 1),
    }[color]


def home_color_for_position(board_size: int, position: Position) -> PlayerColor | None:
    for color in PlayerColor:
        if start_position_for_color(board_size, color) == position:
            return color
    return None


def assign_treasures(player_count: int) -> list[list[TreasureType]]:
    treasure_types = list(TreasureType)
    shuffle(treasure_types)
    return [treasure_types[offset * 6:(offset + 1) * 6] for offset in range(player_count)]
