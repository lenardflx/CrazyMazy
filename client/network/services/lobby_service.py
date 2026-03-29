"""
Service for lobby-related actions. Validates local form input before sending to the server, and records the pending state.
TODO: error refactor needs to be applied here.
"""

from __future__ import annotations

from shared.events import ClientCreateLobbyEvent, ClientJoinGameEvent

from client.network.services._service import RequestService
from client.state.runtime_state import ErrorTarget, PendingRequest


class LobbyService(RequestService):
    """Sends lobby-related requests to the server."""

    def create_lobby(self, player_name: str, board_size: int) -> bool:
        """Validate the form and request the server to create a new lobby.

        :param player_name: The display name the player wants to use.
        :param board_size: The desired board size for the new game.
        """
        name = player_name.strip()
        self._runtime.create_lobby.player_name = name
        self._clear_errors(ErrorTarget.CREATE_LOBBY, ErrorTarget.GLOBAL)

        # Client-side validation before sending to the server
        if not name:
            return self._fail(ErrorTarget.CREATE_LOBBY, "Enter a name.")

        return self._send_request(
            ClientCreateLobbyEvent(board_size=board_size, player_name=name),
            pending=PendingRequest.CREATE_LOBBY,
            error_target=ErrorTarget.CREATE_LOBBY,
        )

    def join_lobby(self, player_name: str, join_code: str) -> bool:
        """Validate the form and request the server to join an existing lobby.

        :param player_name: The display name the player wants to use.
        :param join_code: The lobby join code to connect to.
        """
        name = player_name.strip()
        code = join_code.strip().upper()
        self._runtime.join_lobby.player_name = name
        self._runtime.join_lobby.join_code = code
        self._clear_errors(ErrorTarget.JOIN_LOBBY, ErrorTarget.GLOBAL)

        # Client-side validation before sending to the server
        if not name:
            return self._fail(ErrorTarget.JOIN_LOBBY, "Enter a name.")
        if not code:
            return self._fail(ErrorTarget.JOIN_LOBBY, "Enter a join code.")

        return self._send_request(
            ClientJoinGameEvent(join_code=code, player_name=name),
            pending=PendingRequest.JOIN_LOBBY,
            error_target=ErrorTarget.JOIN_LOBBY,
        )
