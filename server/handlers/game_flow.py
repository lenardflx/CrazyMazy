# Author: Lenard Felix
 
from __future__ import annotations

from collections.abc import Callable
from uuid import UUID

from server.db import game_service
from server.handlers._responses import error_response, left_response, map_value_error_code, snapshot_response
from server.network.dispatch import dispatcher
from server.network.models import OutgoingMessage, RequestContext
from server.service import GameState
from shared.events import (
    ClientCreateLobbyEvent,
    ClientGameEndTurnEvent,
    ClientGameGiveUpEvent,
    ClientGameLeaveEvent,
    ClientGameMovePlayerEvent,
    ClientGameShiftTileEvent,
    ClientGameStartEvent,
    ClientJoinGameEvent,
)
from shared.models import InsertionSide


@dispatcher.handler(ClientCreateLobbyEvent)
def handle_create_lobby(ctx: RequestContext, event: ClientCreateLobbyEvent) -> list[OutgoingMessage]:
    try:
        state = game_service.create_lobby(
            board_size=event.board_size,
            leader_display_name=event.player_name,
            connection_id=ctx.connection_id,
        )
        game_state = game_service.get_game_state(state.game.id)
        if game_state is None:
            raise ValueError("Game not found")
    except ValueError as exc:
        return error_response(ctx, map_value_error_code(str(exc)), str(exc))
    return snapshot_response(game_state)


@dispatcher.handler(ClientJoinGameEvent)
def handle_join_game(ctx: RequestContext, event: ClientJoinGameEvent) -> list[OutgoingMessage]:
    try:
        state = game_service.join_game(
            join_code=event.join_code,
            display_name=event.player_name,
            connection_id=ctx.connection_id,
        )
        game_state = game_service.get_game_state(state.game.id)
        if game_state is None:
            raise ValueError("Game not found")
    except ValueError as exc:
        return error_response(ctx, map_value_error_code(str(exc)), str(exc))
    return snapshot_response(game_state)


@dispatcher.handler(ClientGameStartEvent)
def handle_start_game(ctx: RequestContext, event: ClientGameStartEvent) -> list[OutgoingMessage]:
    del event
    return _handle_connection_game_update(ctx, lambda player_id: game_service.start_game(player_id))


@dispatcher.handler(ClientGameShiftTileEvent)
def handle_shift_tile(ctx: RequestContext, event: ClientGameShiftTileEvent) -> list[OutgoingMessage]:
    return _handle_connection_game_update(
        ctx,
        lambda player_id: game_service.shift_tile(
            player_id,
            InsertionSide(event.insertion_side),
            event.insertion_index,
            event.rotation,
        ),
    )


@dispatcher.handler(ClientGameMovePlayerEvent)
def handle_move_player(ctx: RequestContext, event: ClientGameMovePlayerEvent) -> list[OutgoingMessage]:
    return _handle_connection_game_update(ctx, lambda player_id: game_service.move_player(player_id, event.x, event.y))


@dispatcher.handler(ClientGameEndTurnEvent)
def handle_end_turn(ctx: RequestContext, event: ClientGameEndTurnEvent) -> list[OutgoingMessage]:
    del event
    return _handle_connection_game_update(ctx, lambda player_id: game_service.end_turn(player_id))


@dispatcher.handler(ClientGameGiveUpEvent)
def handle_give_up(ctx: RequestContext, event: ClientGameGiveUpEvent) -> list[OutgoingMessage]:
    del event
    return _handle_departure_game_update(ctx, lambda player_id: game_service.give_up(player_id), "GAVE_UP")


@dispatcher.handler(ClientGameLeaveEvent)
def handle_leave_game(ctx: RequestContext, event: ClientGameLeaveEvent) -> list[OutgoingMessage]:
    del event
    return _handle_departure_game_update(ctx, lambda player_id: game_service.leave_game(player_id), "LEFT_GAME")


def _handle_connection_game_update(
    ctx: RequestContext,
    fn: Callable[[UUID], GameState],
) -> list[OutgoingMessage]:
    state = game_service.get_connection_state(ctx.connection_id)
    if state is None:
        return error_response(ctx, map_value_error_code("Player not found"), "Player not found")
    try:
        game_state = fn(state.player.id)
    except ValueError as exc:
        return error_response(ctx, map_value_error_code(str(exc)), str(exc))
    return snapshot_response(game_state)


def _handle_optional_connection_game_update(
    ctx: RequestContext,
    fn: Callable[[UUID], GameState | None],
) -> list[OutgoingMessage]:
    state = game_service.get_connection_state(ctx.connection_id)
    if state is None:
        return error_response(ctx, map_value_error_code("Player not found"), "Player not found")
    try:
        game_state = fn(state.player.id)
    except ValueError as exc:
        return error_response(ctx, map_value_error_code(str(exc)), str(exc))
    if game_state is None:
        return []
    return snapshot_response(game_state)


def _handle_departure_game_update(
    ctx: RequestContext,
    fn: Callable[[UUID], GameState | None],
    reason: str,
) -> list[OutgoingMessage]:
    state = game_service.get_connection_state(ctx.connection_id)
    if state is None:
        return error_response(ctx, map_value_error_code("Player not found"), "Player not found")
    try:
        game_state = fn(state.player.id)
    except ValueError as exc:
        return error_response(ctx, map_value_error_code(str(exc)), str(exc))
    outgoing = left_response(ctx, reason)
    if game_state is not None:
        outgoing.extend(snapshot_response(game_state))
    return outgoing
