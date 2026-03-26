# Author: Lenard Felix
# TODO: Split up file and add documentation

from __future__ import annotations

from shared.events import Event
from shared.events import (
    ClientCreateLobbyEvent,
    ClientGameLeaveEvent,
    ClientGameGiveUpEvent,
    ClientGameMovePlayerEvent,
    ClientGameShiftTileEvent,
    ClientGameStartEvent,
    ClientJoinGameEvent,
)
from shared.models import InsertionSide

from client.network.client_connection import ClientConnection
from client.state.runtime_state import ErrorTarget, PendingRequest, RuntimeState


def request_create_lobby(connection: ClientConnection, runtime: RuntimeState, player_name: str, board_size: int) -> bool:
    name = player_name.strip()
    runtime.create_lobby.player_name = name
    runtime.create_lobby.error_message = None
    runtime.global_error_message = None

    if not name:
        runtime.create_lobby.error_message = "Enter a name."
        return False
    if not connection.is_connected:
        runtime.create_lobby.error_message = "Not connected to the server."
        return False

    return _send_request(
        connection,
        runtime,
        ClientCreateLobbyEvent(board_size=board_size, player_name=name),
        pending=PendingRequest.CREATE_LOBBY,
        error_target=ErrorTarget.CREATE_LOBBY,
        disconnected_message="Not connected to the server.",
    )


def request_join_lobby(connection: ClientConnection, runtime: RuntimeState, player_name: str, join_code: str) -> bool:
    name = player_name.strip()
    code = join_code.strip().upper()
    runtime.join_lobby.player_name = name
    runtime.join_lobby.join_code = code
    runtime.join_lobby.error_message = None
    runtime.global_error_message = None

    if not name:
        runtime.join_lobby.error_message = "Enter a name."
        return False
    if not code:
        runtime.join_lobby.error_message = "Enter a join code."
        return False
    if not connection.is_connected:
        runtime.join_lobby.error_message = "Not connected to the server."
        return False

    return _send_request(
        connection,
        runtime,
        ClientJoinGameEvent(join_code=code, player_name=name),
        pending=PendingRequest.JOIN_LOBBY,
        error_target=ErrorTarget.JOIN_LOBBY,
        disconnected_message="Not connected to the server.",
    )


def request_start_game(connection: ClientConnection, runtime: RuntimeState) -> bool:
    runtime.global_error_message = None
    return _send_request(
        connection,
        runtime,
        ClientGameStartEvent(),
        pending=PendingRequest.START_GAME,
        error_target=ErrorTarget.GLOBAL,
        disconnected_message="Not connected to the server.",
    )


def request_shift_tile(connection: ClientConnection, runtime: RuntimeState, side: InsertionSide, index: int, rotation: int) -> bool:
    runtime.game.error_message = None
    return _send_request(
        connection,
        runtime,
        ClientGameShiftTileEvent(
            insertion_side=side.value,
            insertion_index=index,
            rotation=rotation,
        ),
        pending=PendingRequest.SHIFT_TILE,
        error_target=ErrorTarget.GAME,
        disconnected_message="Not connected to the server.",
    )


def request_move_player(connection: ClientConnection, runtime: RuntimeState, x: int, y: int) -> bool:
    runtime.game.error_message = None
    return _send_request(
        connection,
        runtime,
        ClientGameMovePlayerEvent(x=x, y=y),
        pending=PendingRequest.MOVE_PLAYER,
        error_target=ErrorTarget.GAME,
        disconnected_message="Not connected to the server.",
    )


def request_give_up(connection: ClientConnection, runtime: RuntimeState) -> bool:
    runtime.game.error_message = None
    return _send_request(
        connection,
        runtime,
        ClientGameGiveUpEvent(),
        pending=PendingRequest.GIVE_UP,
        error_target=ErrorTarget.GAME,
        disconnected_message="Not connected to the server.",
    )


def request_leave_game(connection: ClientConnection, runtime: RuntimeState, *, in_game: bool) -> bool:
    target = ErrorTarget.GAME if in_game else ErrorTarget.GLOBAL
    if in_game:
        runtime.game.error_message = None
    else:
        runtime.global_error_message = None
    return _send_request(
        connection,
        runtime,
        ClientGameLeaveEvent(),
        pending=PendingRequest.LEAVE_GAME,
        error_target=target,
        disconnected_message="Not connected to the server.",
    )


def _send_request(
    connection: ClientConnection,
    runtime: RuntimeState,
    event: Event,
    *,
    pending: PendingRequest,
    error_target: ErrorTarget,
    disconnected_message: str,
) -> bool:
    if not connection.is_connected:
        _set_error(runtime, error_target, disconnected_message)
        return False
    if not connection.send_event(event):
        _set_error(runtime, error_target, disconnected_message)
        return False
    runtime.set_pending(pending, error_target)
    return True


def _set_error(runtime: RuntimeState, target: ErrorTarget, message: str) -> None:
    if target == ErrorTarget.CREATE_LOBBY:
        runtime.create_lobby.error_message = message
        return
    if target == ErrorTarget.JOIN_LOBBY:
        runtime.join_lobby.error_message = message
        return
    if target == ErrorTarget.GAME:
        runtime.game.error_message = message
        return
    runtime.global_error_message = message
