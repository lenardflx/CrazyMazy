from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from shared.types.enums import InsertionSide, TreasureType
from shared.lib.lobby import VALID_BOARD_SIZES

# TODO: docs after error handling is refactored

class PendingRequest(StrEnum):
    CREATE_LOBBY = "CREATE_LOBBY"
    JOIN_LOBBY = "JOIN_LOBBY"
    START_GAME = "START_GAME"
    ADD_NPC = "ADD_NPC"
    SHIFT_TILE = "SHIFT_TILE"
    MOVE_PLAYER = "MOVE_PLAYER"
    GIVE_UP = "GIVE_UP"
    LEAVE_GAME = "LEAVE_GAME"


# TODO: I dont like this error handling at all... any ideas?
class ErrorTarget(StrEnum):
    CREATE_LOBBY = "CREATE_LOBBY"
    JOIN_LOBBY = "JOIN_LOBBY"
    GLOBAL = "GLOBAL"
    GAME = "GAME"


@dataclass(slots=True)
class CreateLobbyFormState:
    """Persists form inputs and validation errors for the create-lobby screen across re-renders."""
    player_name: str = ""
    board_size: int = min(VALID_BOARD_SIZES)
    error_message: str | None = None


@dataclass(slots=True)
class JoinLobbyFormState:
    """Persists form inputs and validation errors for the join-lobby screen across re-renders."""
    player_name: str = ""
    join_code: str = ""
    error_message: str | None = None


@dataclass(slots=True)
class BoardShiftAnimation:
    """Client-side animation state for a board row/column shift. Advanced each frame by the game screen."""

    side: InsertionSide
    index: int
    progress: float = 0.0
    duration: float = 0.18  # seconds

    @property
    def is_finished(self) -> bool:
        return self.progress >= 1.0

    @property
    def eased_progress(self) -> float:
        """Returns an ease-out version of the raw progress value for smoother animation."""
        clamped = min(max(self.progress, 0.0), 1.0)
        return 1.0 - (1.0 - clamped) * (1.0 - clamped)

    def advance(self, dt: float) -> None:
        """Advance the animation by the given delta time in seconds."""
        if self.duration <= 0:
            self.progress = 1.0
            return
        self.progress = min(1.0, self.progress + (dt / self.duration))


@dataclass(slots=True)
class PlayerMoveAnimation:
    """Client-side animation state for a player movement along a path. Advanced each frame by the game screen."""

    player_id: str
    path: list[tuple[int, int]]
    collected_treasure_type: TreasureType | None = None  # Set if the player collected a treasure during this move
    progress: float = 0.0
    duration_per_step: float = 0.16  # seconds per path step

    @property
    def is_finished(self) -> bool:
        return self.progress >= 1.0

    @property
    def eased_progress(self) -> float:
        """Returns an ease-out version of the raw progress value for smoother animation."""
        clamped = min(max(self.progress, 0.0), 1.0)
        return 1.0 - (1.0 - clamped) * (1.0 - clamped)

    @property
    def duration(self) -> float:
        """Total animation duration in seconds, scaled by the number of steps in the path."""
        return max(0.01, max(1, len(self.path) - 1) * self.duration_per_step)

    def advance(self, dt: float) -> None:
        """Advance the animation by the given delta time in seconds."""
        self.progress = min(1.0, self.progress + (dt / self.duration))


@dataclass(slots=True)
class GameRuntimeState:
    """Holds mutable in-game client state that is not derived from the server snapshot."""
    spare_rotation: int = 0  # The current local rotation of the spare tile (0–3)
    error_message: str | None = None
    shift_animation: BoardShiftAnimation | None = None
    move_animation: PlayerMoveAnimation | None = None


@dataclass(slots=True)
class RuntimeState:
    """
    Top-level mutable client state that lives for the entire session.
    Aggregates form state, in-game state, error messages, and the currently pending server request.
    """
    create_lobby: CreateLobbyFormState = field(default_factory=CreateLobbyFormState)
    join_lobby: JoinLobbyFormState = field(default_factory=JoinLobbyFormState)
    game: GameRuntimeState = field(default_factory=GameRuntimeState)
    global_error_message: str | None = None
    pending_request: PendingRequest | None = None
    pending_error_target: ErrorTarget | None = None

    def clear_errors(self) -> None:
        """Clear all error messages across all sub-states."""
        self.create_lobby.error_message = None
        self.join_lobby.error_message = None
        self.game.error_message = None
        self.global_error_message = None

    def clear_pending(self) -> None:
        """Clear the pending request tracking, typically called when a server response arrives."""
        self.pending_request = None
        self.pending_error_target = None

    def set_pending(self, request: PendingRequest, target: ErrorTarget) -> None:
        """Record that a request has been sent and we are waiting for a response.

        :param request: The type of request that is in flight.
        :param target: Where to route the error if the server responds with a failure.
        """
        self.pending_request = request
        self.pending_error_target = target
