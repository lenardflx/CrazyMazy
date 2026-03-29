# Author: Lenard Felix
 
from __future__ import annotations

from collections.abc import Callable
from uuid import UUID

from server.db import game_service
from server.handlers._responses import error_response, left_response, snapshot_response
from server.network.dispatch import dispatcher
from server.network.models import OutgoingMessage, RequestContext
from shared.game.state import GameState
from shared.events import (
    ClientCreateLobbyEvent,
    ClientGameAddNpcEvent,
    ClientGameEndTurnEvent,
    ClientGameGiveUpEvent,
    ClientGameLeaveEvent,
    ClientGameMovePlayerEvent,
    ClientGameShiftTileEvent,
    ClientGameStartEvent,
    ClientJoinGameEvent,
)
from shared.types.enums import InsertionSide
from shared.models import InsertionSide
from shared.protocol import ErrorCode


@dispatcher.handler(ClientCreateLobbyEvent)
def handle_create_lobby(ctx: RequestContext, event: ClientCreateLobbyEvent) -> list[OutgoingMessage]:
    state = game_service.create_lobby(
        board_size=event.board_size,
        leader_display_name=event.player_name,
        connection_id=ctx.connection_id,
    )
    game_state = game_service.get_game_state(state.game.id)
    if game_state is None:
        return error_response(ctx, ErrorCode.GAME_NOT_FOUND)
    return snapshot_response(game_state)


@dispatcher.handler(ClientJoinGameEvent)
def handle_join_game(ctx: RequestContext, event: ClientJoinGameEvent) -> list[OutgoingMessage]:
    state = game_service.join_game(
        join_code=event.join_code,
        display_name=event.player_name,
        connection_id=ctx.connection_id,
    )
    if isinstance(state, ErrorCode):
        return error_response(ctx, state)
    game_state = game_service.get_game_state(state.game.id)
    if game_state is None:
        return error_response(ctx, ErrorCode.GAME_NOT_FOUND)
    return snapshot_response(game_state)


@dispatcher.handler(ClientGameStartEvent)
def handle_start_game(ctx: RequestContext, event: ClientGameStartEvent) -> list[OutgoingMessage]:
    del event
    return _handle_connection_game_update(ctx, lambda player_id: game_service.start_game(player_id))


@dispatcher.handler(ClientGameAddNpcEvent)
def handle_add_npc(ctx: RequestContext, event: ClientGameAddNpcEvent) -> list[OutgoingMessage]:
    return _handle_connection_game_update(ctx, lambda player_id: game_service.add_npc(player_id, event.difficulty))


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
def handle_end_turn(ctx: RequestContext, _: ClientGameEndTurnEvent) -> list[OutgoingMessage]:
    return _handle_connection_game_update(ctx, lambda player_id: game_service.end_turn(player_id))


@dispatcher.handler(ClientGameGiveUpEvent)
def handle_give_up(ctx: RequestContext, _: ClientGameGiveUpEvent) -> list[OutgoingMessage]:
    return _handle_optional_connection_game_update(ctx, lambda player_id: game_service.give_up(player_id))


@dispatcher.handler(ClientGameLeaveEvent)
def handle_leave_game(ctx: RequestContext, _: ClientGameLeaveEvent) -> list[OutgoingMessage]:
    return _handle_departure_game_update(ctx, lambda player_id: game_service.leave_game(player_id), "LEFT_GAME")


def _handle_connection_game_update(
    ctx: RequestContext,
    fn: Callable[[UUID], GameState],
) -> list[OutgoingMessage]:
    state = game_service.get_connection_state(ctx.connection_id)
    if state is None:
        return error_response(ctx, ErrorCode.PLAYER_NOT_FOUND)

    game_state = fn(state.player.id)

    if isinstance(game_state, ErrorCode):
        return error_response(ctx, game_state)
    outgoing = snapshot_response(game_state)
    game_service.schedule_npc_turns(game_state)
    return outgoing


def _handle_optional_connection_game_update(
    ctx: RequestContext,
    fn: Callable[[UUID], GameState | None],
) -> list[OutgoingMessage]:
    state = game_service.get_connection_state(ctx.connection_id)
    if state is None:
        return error_response(ctx, ErrorCode.GAME_NOT_FOUND)
    game_state = fn(state.player.id)
    if isinstance(game_state, ErrorCode):
        return error_response(ctx, game_state)
    if game_state is None:
        return []
    outgoing = snapshot_response(game_state)
    game_service.schedule_npc_turns(game_state)
    return outgoing


def _handle_departure_game_update(
    ctx: RequestContext,
    fn: Callable[[UUID], GameState | None],
    reason: str,
) -> list[OutgoingMessage]:
    state = game_service.get_connection_state(ctx.connection_id)
    if state is None:
        return error_response(ctx, ErrorCode.PLAYER_NOT_FOUND)
    game_state = fn(state.player.id)
    if isinstance(game_state, ErrorCode):
        return error_response(ctx, game_state)
    outgoing = left_response(ctx, reason)
    if game_state is not None:
        outgoing.extend(snapshot_response(game_state))
        game_service.schedule_npc_turns(game_state)
    return outgoing
