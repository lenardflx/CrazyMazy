from __future__ import annotations

from client.state.runtime_state import PendingRequest, RuntimeState
from shared.protocol import ErrorCode
from shared.schema import ErrorPayload


def apply_server_error(runtime: RuntimeState, error: ErrorPayload) -> None:
    pending_request = runtime.pending_request
    runtime.clear_pending()
    message = error["message"]
    if pending_request == PendingRequest.CREATE_LOBBY:
        runtime.create_lobby.error_message = _form_error_message(error)
        return
    if pending_request == PendingRequest.JOIN_LOBBY:
        runtime.join_lobby.error_message = _form_error_message(error)
        return
    runtime.global_error_message = message


def _form_error_message(error: ErrorPayload) -> str:
    code = error["code"]
    if code == ErrorCode.DISPLAY_NAME_TAKEN:
        return "Name already taken."
    if code == ErrorCode.GAME_NOT_FOUND or code == ErrorCode.GAME_NOT_JOINABLE:
        return "Join code not found."
    if code == ErrorCode.INVALID_BOARD_SIZE:
        return "Choose a valid board size."
    return error["message"]
