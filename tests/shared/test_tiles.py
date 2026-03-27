from shared.types.enums import InsertionSide, TileOrientation, TileType
from shared.game.board import Board
from shared.game.tile import Tile


def test_tile_paths_for_corner_orientation() -> None:
    tile = Tile(TileType.CORNER, TileOrientation.EAST)
    assert tile.path == [0, 1, 1, 0]


def test_tile_rotate_left_updates_orientation_and_paths() -> None:
    tile = Tile(TileType.T, TileOrientation.SOUTH)
    tile.rotate_left()
    assert tile.orientation == TileOrientation.EAST
    assert tile.path == [1, 1, 1, 0]


def test_tile_rotate_right_updates_orientation_and_paths() -> None:
    tile = Tile(TileType.STRAIGHT, TileOrientation.NORTH)
    tile.rotate_right()
    assert tile.orientation == TileOrientation.EAST
    assert tile.path == [0, 1, 0, 1]


def test_board_from_payloads_requires_spare_tile() -> None:
    try:
        Board.from_payloads(
            7,
            [
                {
                    "id": "tile-1",
                    "tile_type": TileType.CORNER,
                    "rotation": 0,
                    "is_spare": False,
                    "treasure_type": None,
                    "row": 0,
                    "column": 0,
                }
            ],
        )
    except ValueError as exc:
        assert str(exc) == "Board payload contains no spare tile"
    else:
        raise AssertionError("Expected Board.from_payloads to reject payloads without a spare tile")


def test_board_from_payloads_rejects_multiple_spare_tiles() -> None:
    try:
        Board.from_payloads(
            7,
            [
                {
                    "id": "tile-1",
                    "tile_type": TileType.CORNER,
                    "rotation": 0,
                    "is_spare": True,
                    "treasure_type": None,
                },
                {
                    "id": "tile-2",
                    "tile_type": TileType.T,
                    "rotation": 1,
                    "is_spare": True,
                    "treasure_type": None,
                },
            ],
        )
    except ValueError as exc:
        assert str(exc) == "Board payload contains multiple spare tiles"
    else:
        raise AssertionError("Expected Board.from_payloads to reject payloads with multiple spare tiles")


def test_board_shift_tile_applies_rotation_relative_to_current_spare_orientation() -> None:
    board = Board(7)
    board.create_blocked_board()
    board.spare = Tile(TileType.CORNER, TileOrientation.SOUTH)

    board.shift_tile(InsertionSide.LEFT, 1, 1)

    inserted_tile = board.tiles[(0, 1)]
    assert inserted_tile is not None
    assert inserted_tile.orientation == TileOrientation.WEST
