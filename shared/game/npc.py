from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from shared.types.enums import InsertionSide, NpcDifficulty

if TYPE_CHECKING:
    from shared.game.state import GameState


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
        game_state: "GameState",
        blocked_side: InsertionSide | None = None,
        blocked_index: int | None = None,
    ) -> NpcTurn:
        """Choose a full deterministic turn plan for the current board state."""

        if game_state.board is None:
            raise ValueError("NPC cannot choose a turn without a board")
        
        # for now its dumb. TODO: make it smart :D
        insert_index = 3 if blocked_index != 3 else 1

        return NpcTurn(
            shift_side=InsertionSide.LEFT,
            shift_index=insert_index,
            shift_rotation=0,
            move_to=None,
        )
