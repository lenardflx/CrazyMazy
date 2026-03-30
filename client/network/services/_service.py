from __future__ import annotations

from shared.events import Event

from client.network.client_connection import ClientConnection
from client.state.runtime_state import ErrorTarget, PendingRequest, RuntimeState


_DISCONNECTED = "Not connected to the server."


class RequestService:
    """Shared base for LobbyService and GameService."""

    def __init__(self, connection: ClientConnection, runtime: RuntimeState) -> None:
        self._connection = connection
        self._runtime = runtime

    def _send_request(
        self,
        event: Event,
        *,
        pending: PendingRequest,
        error_target: ErrorTarget,
    ) -> bool:
        if not self._connection.is_connected or not self._connection.send_event(event):
            return self._fail(error_target, _DISCONNECTED)
        self._runtime.set_pending(pending, error_target)
        return True

    def _fail(self, target: ErrorTarget, message: str) -> bool:
        self._set_error(target, message)
        return False

    def _clear_errors(self, *targets: ErrorTarget) -> None:
        for target in targets:
            self._set_error(target, None)

    def _set_error(self, target: ErrorTarget, message: str | None) -> None:
        if target == ErrorTarget.CREATE_LOBBY:
            self._runtime.create_lobby.error_message = message
            return
        if target == ErrorTarget.JOIN_LOBBY:
            self._runtime.join_lobby.error_message = message
            return
        if target == ErrorTarget.GAME:
            self._runtime.game.error_message = message
            return
        self._runtime.global_error_message = message
