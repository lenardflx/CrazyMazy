# Author: Lenard Felix

from __future__ import annotations

from server.db import game_service
from server.handlers._responses import error_response, map_value_error_code, snapshot_response
from server.network.dispatch import dispatcher
from server.network.models import OutgoingMessage, RequestContext
from shared.events import ClientJoinGameEvent


@dispatcher.handler(ClientJoinGameEvent)
def handle_join_game(ctx: RequestContext, event: ClientJoinGameEvent) -> list[OutgoingMessage]:
    try:
        state = game_service.join_game(
            join_code=event.join_code,
            display_name=event.player_name,
            connection_id=ctx.connection_id,
        )
    except ValueError as exc:
        return error_response(ctx, map_value_error_code(str(exc)), str(exc))

    game_state = game_service.get_game_state(state.game.id)
    if game_state is None:
        return error_response(ctx, map_value_error_code("Game is not joinable"), "Game is not joinable.")
    return snapshot_response(ctx, game_state, viewer_player_id=str(state.player.id))
