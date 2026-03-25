from __future__ import annotations

from shared.events import (
    ClientCreateLobbyEvent,
    ClientGameGiveUpEvent,
    ClientGameMovePlayerEvent,
    ClientGameShiftTileEvent,
    ClientGameStartEvent,
    ClientJoinGameEvent,
)
from shared.models import InsertionSide

from client.network.client_connection import ClientConnection
from client.state.runtime_state import PendingRequest, RuntimeState


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

    connection.send_event(ClientCreateLobbyEvent(board_size=board_size, player_name=name))
    runtime.pending_request = PendingRequest.CREATE_LOBBY
    return True


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

    connection.send_event(ClientJoinGameEvent(join_code=code, player_name=name))
    runtime.pending_request = PendingRequest.JOIN_LOBBY
    return True


def request_start_game(connection: ClientConnection, runtime: RuntimeState) -> bool:
    runtime.global_error_message = None
    if not connection.is_connected:
        runtime.global_error_message = "Not connected to the server."
        return False
    connection.send_event(ClientGameStartEvent())
    return True


def request_shift_tile(connection: ClientConnection, runtime: RuntimeState, side: InsertionSide, index: int, rotation: int) -> bool:
    runtime.game.error_message = None
    if not connection.is_connected:
        runtime.game.error_message = "Not connected to the server."
        return False
    connection.send_event(
        ClientGameShiftTileEvent(
            insertion_side=side.value,
            insertion_index=index,
            rotation=rotation,
        )
    )
    return True


def request_move_player(connection: ClientConnection, runtime: RuntimeState, x: int, y: int) -> bool:
    runtime.game.error_message = None
    if not connection.is_connected:
        runtime.game.error_message = "Not connected to the server."
        return False
    connection.send_event(ClientGameMovePlayerEvent(x=x, y=y))
    return True


def request_give_up(connection: ClientConnection, runtime: RuntimeState) -> bool:
    runtime.game.error_message = None
    if not connection.is_connected:
        runtime.game.error_message = "Not connected to the server."
        return False
    connection.send_event(ClientGameGiveUpEvent())
    return True
