from __future__ import annotations

from shared.events import (
    ClientGameGiveUpEvent,
    ClientGameLeaveEvent,
    ClientGameMovePlayerEvent,
    ClientGameShiftTileEvent,
    ClientGameStartEvent,
)
from shared.types.enums import InsertionSide

from client.network.services._service import RequestService
from client.state.runtime_state import ErrorTarget, PendingRequest


class GameService(RequestService):
    def start_game(self) -> bool:
        self._clear_errors(ErrorTarget.GLOBAL)
        return self._send_request(
            ClientGameStartEvent(),
            pending=PendingRequest.START_GAME,
            error_target=ErrorTarget.GLOBAL,
        )

    def shift_tile(self, side: InsertionSide, index: int, rotation: int) -> bool:
        self._clear_errors(ErrorTarget.GAME)
        return self._send_request(
            ClientGameShiftTileEvent(
                insertion_side=side.value,
                insertion_index=index,
                rotation=rotation,
            ),
            pending=PendingRequest.SHIFT_TILE,
            error_target=ErrorTarget.GAME,
        )

    def move_player(self, x: int, y: int) -> bool:
        self._clear_errors(ErrorTarget.GAME)
        return self._send_request(
            ClientGameMovePlayerEvent(x=x, y=y),
            pending=PendingRequest.MOVE_PLAYER,
            error_target=ErrorTarget.GAME,
        )

    def give_up(self) -> bool:
        self._clear_errors(ErrorTarget.GAME)
        return self._send_request(
            ClientGameGiveUpEvent(),
            pending=PendingRequest.GIVE_UP,
            error_target=ErrorTarget.GAME,
        )

    def leave_game(self, *, in_game: bool) -> bool:
        target = ErrorTarget.GAME if in_game else ErrorTarget.GLOBAL
        self._clear_errors(target)
        return self._send_request(
            ClientGameLeaveEvent(),
            pending=PendingRequest.LEAVE_GAME,
            error_target=target,
        )
