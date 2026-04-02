from uuid import uuid4

from shared.game.board import Board
from shared.game.tile import Tile
from shared.game.npc import Npc
from shared.lib.names import generate_display_name
from shared.types.enums import NpcDifficulty, TileOrientation, TileType


def _make_simple_board() -> Board:
    board = Board(7)
    board.create_blocked_board()
    for x in range(board.width):
        board.change_tile(x, 3, Tile(TileType.STRAIGHT, TileOrientation.EAST))
    board.spare = Tile(TileType.STRAIGHT, TileOrientation.EAST)
    return board


def test_npc_choose_turn_returns_turn_for_valid_board_state() -> None:
    npc = Npc(player_id=uuid4(), difficulty=NpcDifficulty.NORMAL)
    board = _make_simple_board()

    turn = npc.choose_turn(board, current_position=(1, 3), target_position=(5, 3))

    assert turn.shift_index in {1, 3, 5}
    assert 0 <= turn.shift_rotation <= 3


def test_npc_choose_turn_rejects_missing_current_position() -> None:
    npc = Npc(player_id=uuid4(), difficulty=NpcDifficulty.NORMAL)
    board = _make_simple_board()

    try:
        npc.choose_turn(board, current_position=None, target_position=(5, 3))
    except ValueError as exc:
        assert str(exc) == "NPC turn requires a current position"
    else:
        raise AssertionError("expected ValueError")


def test_npc_generates_unique_name_from_existing_names() -> None:
    first = generate_display_name()
    second = generate_display_name({first})

    assert first != second
