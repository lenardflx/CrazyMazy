from __future__ import annotations

from client.state.runtime_state import ErrorTarget, RuntimeState
from shared.protocol import ErrorCode
from shared.schema import ErrorPayload


def apply_server_error(runtime: RuntimeState, error: ErrorPayload) -> None:
    pending_target = runtime.pending_error_target
    runtime.clear_pending()
    message = error["message"]
    if pending_target == ErrorTarget.CREATE_LOBBY:
        runtime.create_lobby.error_message = _form_error_message(error)
        return
    if pending_target == ErrorTarget.JOIN_LOBBY:
        runtime.join_lobby.error_message = _form_error_message(error)
        return
    if pending_target == ErrorTarget.GAME:
        runtime.game.error_message = message
        return
    runtime.global_error_message = message


# TODO: temp implementation, needs to be replaced by proper error handling
def _form_error_message(error: ErrorPayload) -> str:
    code = error["code"]
    if code == ErrorCode.DISPLAY_NAME_TAKEN:
        return "Name already taken."
    if code == ErrorCode.GAME_NOT_FOUND or code == ErrorCode.GAME_NOT_JOINABLE:
        return "Join code not found."
    if code == ErrorCode.INVALID_BOARD_SIZE:
        return "Choose a valid board size."
    return error["message"]
