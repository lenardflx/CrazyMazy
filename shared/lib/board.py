# Author: Lenard Felix

from __future__ import annotations

import random
from collections import deque
from typing import Iterable

from shared.models import InsertionSide, PlayerColor, TileData, TileType, TreasureType

_BASE_OPENINGS: dict[TileType, tuple[bool, bool, bool, bool]] = {
    TileType.STRAIGHT: (True, False, True, False),
    TileType.CORNER: (True, True, False, False),
    TileType.T: (True, True, False, True),
}

_TREASURE_TYPES = list(TreasureType)


def start_position_for_color(board_size: int, color: PlayerColor) -> tuple[int, int]:
    """Return the (x, y) home-corner position for the given player color."""
    return {
        PlayerColor.RED: (0, 0),
        PlayerColor.BLUE: (board_size - 1, 0),
        PlayerColor.GREEN: (0, board_size - 1),
        PlayerColor.YELLOW: (board_size - 1, board_size - 1),
    }[color]


def create_board_tiles(game_id: object, board_size: int) -> list[TileData]:
    """Generate a full set of randomised board tiles plus one spare tile for a new game."""
    fixed_positions = {(row, col) for row in range(0, board_size, 2) for col in range(0, board_size, 2)}
    tiles: list[TileData] = []
    treasure_iter = iter(_TREASURE_TYPES)

    # TODO: we need to split this up and also randomize the treasure placement across the board and spare tile. This is just for testing rn
    for row in range(board_size):
        for col in range(board_size):
            tile_type, rotation = _tile_layout_for_position(board_size, row, col, fixed_positions)
            treasure_type = None
            if (row, col) not in _start_corner_positions(board_size):
                treasure_type = next(treasure_iter, None)
            tiles.append(
                TileData(
                    game_id=game_id, # TODO: fix error
                    row=row,
                    column=col,
                    rotation=rotation,
                    tile_type=tile_type,
                    treasure_type=treasure_type,
                    is_spare=False,
                )
            )

    spare_tile = TileData(
        game_id=game_id, # TODO: fix error
        row=None,
        column=None,
        rotation=random.randint(0, 3),
        tile_type=random.choice((TileType.STRAIGHT, TileType.CORNER, TileType.T)),
        treasure_type=next(treasure_iter, None),
        is_spare=True,
    )
    tiles.append(spare_tile)
    return tiles

def openings(tile_type: TileType, rotation: int) -> tuple[bool, bool, bool, bool]:
    """Return the four directional openings (N, E, S, W) for a tile type at the given rotation."""
    values = deque(_BASE_OPENINGS[tile_type])
    values.rotate(rotation)
    return tuple(values) # TODO: why error? :(


def reachable_positions(board: dict[tuple[int, int], TileData], start: tuple[int, int]) -> set[tuple[int, int]]:
    """Return all positions reachable from ``start`` by following connected tile openings."""
    pending = [start]
    visited: set[tuple[int, int]] = set()

    while pending:
        position = pending.pop()
        if position in visited:
            continue
        visited.add(position)
        tile = board[position]
        current_openings = openings(tile.tile_type, tile.rotation)
        for direction, neighbour in _neighbours(position).items():
            other = board.get(neighbour)
            if other is None or not current_openings[direction]:
                continue
            if not openings(other.tile_type, other.rotation)[(direction + 2) % 4]:
                continue
            pending.append(neighbour)

    return visited


# TODO: this can probably be optimized
def shift_tiles(
    tiles: list[TileData],
    *,
    board_size: int,
    side: InsertionSide,
    index: int,
    rotation: int,
) -> TileData:
    """Insert the spare tile into a row or column, shifting existing tiles and returning the pushed-out tile."""
    board, spare_tile = split_board_tiles(tiles)
    spare_tile.rotation = rotation % 4
    outgoing: TileData

    if side == InsertionSide.LEFT:
        outgoing = board[(board_size - 1, index)]
        for col in range(board_size - 1, 0, -1):
            board[(col, index)] = board[(col - 1, index)]
            board[(col, index)].column = col
        board[(0, index)] = spare_tile
        spare_tile.row = index
        spare_tile.column = 0
    elif side == InsertionSide.RIGHT:
        outgoing = board[(0, index)]
        for col in range(board_size - 1):
            board[(col, index)] = board[(col + 1, index)]
            board[(col, index)].column = col
        board[(board_size - 1, index)] = spare_tile
        spare_tile.row = index
        spare_tile.column = board_size - 1
    elif side == InsertionSide.TOP:
        outgoing = board[(index, board_size - 1)]
        for row in range(board_size - 1, 0, -1):
            board[(index, row)] = board[(index, row - 1)]
            board[(index, row)].row = row
        board[(index, 0)] = spare_tile
        spare_tile.row = 0
        spare_tile.column = index
    else:
        outgoing = board[(index, 0)]
        for row in range(board_size - 1):
            board[(index, row)] = board[(index, row + 1)]
            board[(index, row)].row = row
        board[(index, board_size - 1)] = spare_tile
        spare_tile.row = board_size - 1
        spare_tile.column = index

    outgoing.row = None
    outgoing.column = None
    outgoing.is_spare = True
    spare_tile.is_spare = False
    return outgoing


def shift_player_position(
    position: tuple[int, int] | None,
    *,
    board_size: int,
    side: InsertionSide,
    index: int,
) -> tuple[int, int] | None:
    """Return the new position after a shift, wrapping around if pushed off the board, or ``None`` if unaffected."""
    if position is None:
        return None
    x, y = position
    if side in (InsertionSide.LEFT, InsertionSide.RIGHT) and y != index:
        return position
    if side in (InsertionSide.TOP, InsertionSide.BOTTOM) and x != index:
        return position
    if side == InsertionSide.LEFT:
        return ((x + 1) % board_size, y)
    if side == InsertionSide.RIGHT:
        return ((x - 1) % board_size, y)
    if side == InsertionSide.TOP:
        return (x, (y + 1) % board_size)
    return (x, (y - 1) % board_size)


def opposite_side(side: InsertionSide) -> InsertionSide:
    """Return the insertion side directly opposite the given one."""
    return {
        InsertionSide.TOP: InsertionSide.BOTTOM,
        InsertionSide.RIGHT: InsertionSide.LEFT,
        InsertionSide.BOTTOM: InsertionSide.TOP,
        InsertionSide.LEFT: InsertionSide.RIGHT,
    }[side]


def split_board_tiles(tiles: Iterable[TileData]) -> tuple[dict[tuple[int, int], TileData], TileData]:
    """Split a flat tile list into a ``{(x, y): tile}`` board dict and the spare tile."""
    board: dict[tuple[int, int], TileData] = {}
    spare_tile: TileData | None = None

    for tile in tiles:
        if tile.is_spare:
            spare_tile = tile
            continue
        if tile.row is None or tile.column is None:
            continue
        board[(tile.column, tile.row)] = tile

    # TODO: I had this error, but this should never happen since the board always has a spare tile. Needs to be debugged
    if spare_tile is None:
        raise ValueError("Game board has no spare tile")
    return board, spare_tile


def movable_insertion_indexes(board_size: int) -> tuple[int, ...]:
    """Return all odd-numbered row/column indexes that can accept a tile insertion."""
    return tuple(range(1, board_size, 2))


def is_valid_insertion_index(board_size: int, index: int) -> bool:
    """Return ``True`` if ``index`` is a valid insertion row/column for the board."""
    return index in movable_insertion_indexes(board_size)


def assign_treasures(player_count: int) -> list[list[TreasureType]]:
    """Return a shuffled list of 6-treasure assignments, one sub-list per player."""
    treasure_types = list(_TREASURE_TYPES)
    random.shuffle(treasure_types)
    return [treasure_types[offset * 6:(offset + 1) * 6] for offset in range(player_count)]


def _tile_layout_for_position(
    board_size: int,
    row: int,
    col: int,
    fixed_positions: set[tuple[int, int]],
) -> tuple[TileType, int]:
    """Return the (tile type, rotation) for a position, using fixed layouts for corners and T-junctions."""
    corners = _start_corner_positions(board_size)
    if (row, col) == corners[0]:
        return TileType.CORNER, 1
    if (row, col) == corners[1]:
        return TileType.CORNER, 2
    if (row, col) == corners[2]:
        return TileType.CORNER, 0
    if (row, col) == corners[3]:
        return TileType.CORNER, 3
    if (row, col) in fixed_positions:
        return TileType.T, random.randint(0, 3)
    return random.choice((TileType.STRAIGHT, TileType.CORNER, TileType.T)), random.randint(0, 3)


def _start_corner_positions(board_size: int) -> tuple[tuple[int, int], ...]:
    """Return the four player starting corner positions in (row, col) order."""
    return (
        (0, 0),
        (0, board_size - 1),
        (board_size - 1, 0),
        (board_size - 1, board_size - 1),
    )


def _neighbours(position: tuple[int, int]) -> dict[int, tuple[int, int]]:
    """Return the four adjacent positions keyed by direction index (0=N, 1=E, 2=S, 3=W)."""
    x, y = position
    return {
        0: (x, y - 1),
        1: (x + 1, y),
        2: (x, y + 1),
        3: (x - 1, y),
    }
