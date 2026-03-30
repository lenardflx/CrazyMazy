"""
Service for in-game actions. Each method clears any stale error, sends the request to the server, and records the pending state.
TODO: error refactor needs to be applied here.
"""

from __future__ import annotations

from shared.events import (
    ClientGameAddNpcEvent,
    ClientGameGiveUpEvent,
    ClientGameLeaveEvent,
    ClientGameMovePlayerEvent,
    ClientGameShiftTileEvent,
    ClientGameStartEvent,
)
from shared.types.enums import InsertionSide, NpcDifficulty

from client.network.services._service import RequestService
from client.state.runtime_state import ErrorTarget, PendingRequest


class GameService(RequestService):
    """Sends game-related requests to the server on behalf of the player."""

    def start_game(self) -> bool:
        """Request the server to start the game. Only the lobby leader can do this."""
        self._clear_errors(ErrorTarget.GLOBAL)
        return self._send_request(
            ClientGameStartEvent(),
            pending=PendingRequest.START_GAME,
            error_target=ErrorTarget.GLOBAL,
        )

    def add_npc(self, difficulty: NpcDifficulty = NpcDifficulty.NORMAL) -> bool:
        """Request the server to add an NPC player with the given difficulty to the lobby.

        :param difficulty: The difficulty level of the NPC to add.
        """
        self._clear_errors(ErrorTarget.GLOBAL)
        return self._send_request(
            ClientGameAddNpcEvent(difficulty=difficulty),
            pending=PendingRequest.ADD_NPC,
            error_target=ErrorTarget.GLOBAL,
        )

    def shift_tile(self, side: InsertionSide, index: int, rotation: int) -> bool:
        """Request the server to insert the spare tile at the given board edge position with the given rotation.

        :param side: Which edge of the board to insert from.
        :param index: The column or row index to insert at.
        :param rotation: The clockwise rotation to apply to the spare tile (0–3).
        """
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
        """Request the server to move the local player to the given board coordinates.

        :param x: Target column.
        :param y: Target row.
        """
        self._clear_errors(ErrorTarget.GAME)
        return self._send_request(
            ClientGameMovePlayerEvent(x=x, y=y),
            pending=PendingRequest.MOVE_PLAYER,
            error_target=ErrorTarget.GAME,
        )

    def give_up(self) -> bool:
        """Request the server to mark the local player as having given up, turning them into a spectator."""
        self._clear_errors(ErrorTarget.GAME)
        return self._send_request(
            ClientGameGiveUpEvent(),
            pending=PendingRequest.GIVE_UP,
            error_target=ErrorTarget.GAME,
        )

    def leave_game(self, *, in_game: bool) -> bool:
        """Request the server to remove the local player from the current game or lobby.

        :param in_game: True if the player is leaving during an active match (errors go to the game screen),
            False if leaving from the lobby or post-game screen (errors go to the global banner).
        """
        target = ErrorTarget.GAME if in_game else ErrorTarget.GLOBAL
        self._clear_errors(target)
        return self._send_request(
            ClientGameLeaveEvent(),
            pending=PendingRequest.LEAVE_GAME,
            error_target=target,
        )
