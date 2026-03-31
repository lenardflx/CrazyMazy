from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from shared.game.board import Board, Position
from shared.types.enums import InsertionSide, NpcDifficulty


@dataclass(slots=True, frozen=True)
class NpcTurn:
    shift_side: InsertionSide
    shift_index: int
    shift_rotation: int
    move_to: tuple[int, int] | None = None


@dataclass(slots=True)
class Npc:
    """Represents a non-player character in the game, with logic to choose turns."""

    player_id: UUID
    difficulty: NpcDifficulty = NpcDifficulty.NORMAL

    def choose_turn(
        self,
        board: Board,
        current_position: Position | None,
        target_position: Position | None,
        blocked_side: InsertionSide | None = None,
        blocked_index: int | None = None,
    ) -> NpcTurn:
        """Choose a full deterministic turn plan for the current board state."""
        
        # for now its dumb. TODO: make it smart :D
        insert_index = 3 if blocked_index != 3 else 1

        return NpcTurn(
            shift_side=InsertionSide.LEFT,
            shift_index=insert_index,
            shift_rotation=0,
            move_to=None,
        )
