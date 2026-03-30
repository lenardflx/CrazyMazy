"""
Service for in-game actions. Each method clears any stale error, sends the request to the server, and records the pending state.
TODO: error refactor needs to be applied here.
"""

from __future__ import annotations

from client.network.client_connection import ClientConnection
from client.state.runtime_state import RuntimeState
from shared.events import (
    ClientGameAddNpcEvent,
    ClientGameGiveUpEvent,
    ClientGameLeaveEvent,
    ClientGameMovePlayerEvent,
    ClientGameShiftTileEvent,
    ClientGameStartEvent,
)
from shared.types.enums import InsertionSide, NpcDifficulty

class GameService:
    """Sends game-related requests to the server on behalf of the player."""
    def __init__(self, connection: ClientConnection):
        self._connection = connection

    def start_game(self) -> bool:
        """Request the server to start the game. Only the lobby leader can do this."""
        return self._connection.send_event(
            ClientGameStartEvent()
        )

    def add_npc(self, difficulty: NpcDifficulty = NpcDifficulty.NORMAL) -> bool:
        """Request the server to add an NPC player with the given difficulty to the lobby.

        :param difficulty: The difficulty level of the NPC to add.
        """
        return self._connection.send_event(ClientGameAddNpcEvent(difficulty=difficulty))

    def shift_tile(self, side: InsertionSide, index: int, rotation: int) -> bool:
        """Request the server to insert the spare tile at the given board edge position with the given rotation.

        :param side: Which edge of the board to insert from.
        :param index: The column or row index to insert at.
        :param rotation: The clockwise rotation to apply to the spare tile (0–3).
        """
        return self._connection.send_event(
            ClientGameShiftTileEvent(insertion_side=side.value, insertion_index=index, rotation=rotation)
        )

    def move_player(self, x: int, y: int) -> bool:
        """Request the server to move the local player to the given board coordinates.

        :param x: Target column.
        :param y: Target row.
        """
        return self._connection.send_event(
            ClientGameMovePlayerEvent(x=x, y=y)
        )

    def give_up(self) -> bool:
        """Request the server to mark the local player as having given up, turning them into a spectator."""
        return self._connection.send_event(
            ClientGameGiveUpEvent()
        )

    def leave_game(self, *, in_game: bool) -> bool:
        """Request the server to remove the local player from the current game or lobby.
        """
        return self._connection.send_event(
            ClientGameLeaveEvent(),
        )
