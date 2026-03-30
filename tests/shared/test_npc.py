from types import SimpleNamespace
from uuid import uuid4

from shared.game.board import Board
from shared.game.npc import Npc
from shared.types.enums import InsertionSide


def test_npc_prefers_same_shift_when_unblocked() -> None:
    npc = Npc(player_id=uuid4())
    game_state = SimpleNamespace(board=Board(7))

    turn = npc.choose_turn(game_state)

    assert turn.shift_side == InsertionSide.LEFT
    assert turn.shift_index == 1
    assert turn.shift_rotation == 0
    assert turn.move_to is None


def test_npc_skips_blocked_preferred_shift() -> None:
    npc = Npc(player_id=uuid4())
    game_state = SimpleNamespace(board=Board(7))

    turn = npc.choose_turn(game_state, blocked_side=InsertionSide.LEFT, blocked_index=1)

    assert turn.shift_side == InsertionSide.LEFT
    assert turn.shift_index == 3
    assert turn.shift_rotation == 0


def test_npc_generates_unique_name_from_existing_names() -> None:
    first = Npc.generate_name()
    second = Npc.generate_name({first})

    assert first != second
