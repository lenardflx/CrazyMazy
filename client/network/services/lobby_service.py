"""
Service for lobby-related actions. Validates local form input before sending to the server, and records the pending state.
TODO: error refactor needs to be applied here.
"""

from __future__ import annotations

from client.network.client_connection import ClientConnection
from shared.events import ClientCreateLobbyEvent, ClientJoinGameEvent

from client.state.runtime_state import RuntimeState
from shared.protocol import ErrorCode


class LobbyService:
    """Sends lobby-related requests to the server."""
    def __init__(self, connection: ClientConnection, runtime: RuntimeState):
        self._connection = connection
        self._runtime = runtime

    def create_lobby(self, player_name: str, board_size: int) -> ErrorCode | None:
        """Validate the form and request the server to create a new lobby.

        :param player_name: The display name the player wants to use.
        :param board_size: The desired board size for the new game.
        """
        name = player_name.strip()
        self._runtime.create_lobby.player_name = name

        # Client-side validation before sending to the server
        if not name:
            return ErrorCode.DISPLAY_NAME_NOT_ENTERED

        sent = self._connection.send_event(
            ClientCreateLobbyEvent(board_size=board_size, player_name=name)
        )

        return None if sent else ErrorCode.CONNECTION_ERROR

    def join_lobby(self, player_name: str, join_code: str) -> ErrorCode | None:
        """Validate the form and request the server to join an existing lobby.

        :param player_name: The display name the player wants to use.
        :param join_code: The lobby join code to connect to.
        """
        name = player_name.strip()
        code = join_code.strip().upper()
        self._runtime.join_lobby.player_name = name
        self._runtime.join_lobby.join_code = code

        # Client-side validation before sending to the server
        if not name:
            return ErrorCode.DISPLAY_NAME_NOT_ENTERED
        if not code:
            return ErrorCode.JOIN_CODE_NOT_ENTERED

        sent = self._connection.send_event(
            ClientJoinGameEvent(join_code=code, player_name=name)
        )

        return None if sent else ErrorCode.CONNECTION_ERROR
