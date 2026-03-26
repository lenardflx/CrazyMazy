from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from shared.lib.lobby import VALID_BOARD_SIZES


class PendingRequest(StrEnum):
    CREATE_LOBBY = "CREATE_LOBBY"
    JOIN_LOBBY = "JOIN_LOBBY"
    START_GAME = "START_GAME"
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
    player_name: str = ""
    board_size: int = min(VALID_BOARD_SIZES)
    error_message: str | None = None


@dataclass(slots=True)
class JoinLobbyFormState:
    player_name: str = ""
    join_code: str = ""
    error_message: str | None = None


@dataclass(slots=True)
class GameRuntimeState:
    spare_rotation: int = 0
    error_message: str | None = None


@dataclass(slots=True)
class RuntimeState:
    create_lobby: CreateLobbyFormState = field(default_factory=CreateLobbyFormState)
    join_lobby: JoinLobbyFormState = field(default_factory=JoinLobbyFormState)
    game: GameRuntimeState = field(default_factory=GameRuntimeState)
    global_error_message: str | None = None
    pending_request: PendingRequest | None = None
    pending_error_target: ErrorTarget | None = None

    def clear_errors(self) -> None:
        self.create_lobby.error_message = None
        self.join_lobby.error_message = None
        self.game.error_message = None
        self.global_error_message = None

    def clear_pending(self) -> None:
        self.pending_request = None
        self.pending_error_target = None

    def set_pending(self, request: PendingRequest, target: ErrorTarget) -> None:
        self.pending_request = request
        self.pending_error_target = target
