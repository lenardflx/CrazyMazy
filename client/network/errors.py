# Author: Lenard Felix

from __future__ import annotations

from client.lang import language_service
from client.state.runtime_state import ErrorTarget, RuntimeState
from shared.protocol import ErrorCode


def apply_server_error(runtime: RuntimeState, error: ErrorCode) -> None:
    pending_target = runtime.pending_error_target
    runtime.clear_pending()
    if pending_target == ErrorTarget.CREATE_LOBBY:
        runtime.create_lobby.error_message = language_service.get_message(error)
        return
    if pending_target == ErrorTarget.JOIN_LOBBY:
        runtime.join_lobby.error_message = language_service.get_message(error)
        return
    if pending_target == ErrorTarget.GAME:
        runtime.game.error_message = language_service.get_message(error)
        return
    runtime.global_error_message = language_service.get_message(error)
