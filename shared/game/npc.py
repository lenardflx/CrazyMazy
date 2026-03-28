from __future__ import annotations

from dataclasses import dataclass
from random import shuffle
from typing import TYPE_CHECKING, ClassVar
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

    # A Name is generated from a combination of a prefix and suffix
    _NAME_PREFIXES: ClassVar[tuple[str, ...]] = (
        "Amber",
        "Brass",
        "Cinder",
        "Copper",
        "Ember",
        "Flint",
        "Ivy",
        "Moss",
        "River",
        "Sable",
    )
    _NAME_SUFFIXES: ClassVar[tuple[str, ...]] = (
        "Badger",
        "Fox",
        "Hawk",
        "Lynx",
        "Otter",
        "Raven",
        "Stoat",
        "Viper",
        "Wolf",
        "Wren",
    )

    @classmethod
    def generate_name(cls, taken_names: set[str] | None = None) -> str:
        """Return a deterministic generated name that avoids already used ones."""

        # If taken_names is None, any combination is available.
        if taken_names is None:
            taken_names = set()

        # To add some variability, we shuffle the order of combinations
        shuffled_prefixes = list(cls._NAME_PREFIXES)
        shuffled_suffixes = list(cls._NAME_SUFFIXES)
        shuffle(shuffled_prefixes)
        shuffle(shuffled_suffixes)


        for prefix in shuffled_prefixes:
            for suffix in shuffled_suffixes:
                name = f"{prefix} {suffix}"
                if name not in taken_names:
                    return name

        raise ValueError("No unique names available")

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
        insert_index = 3 if blocked_side is 1 else 1

        return NpcTurn(
            shift_side=InsertionSide.LEFT,
            shift_index=insert_index,
            shift_rotation=0,
            move_to=None,
        )
