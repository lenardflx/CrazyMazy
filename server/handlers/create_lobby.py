from __future__ import annotations

from server.db import game_service
from server.handlers._responses import error_response, map_value_error_code, snapshot_response
from server.network.dispatch import dispatcher
from server.network.models import OutgoingMessage, RequestContext
from shared.events import ClientCreateLobbyEvent


@dispatcher.handler(ClientCreateLobbyEvent)
def handle_create_lobby(ctx: RequestContext, event: ClientCreateLobbyEvent) -> list[OutgoingMessage]:
    try:
        state = game_service.create_lobby(
            board_size=event.board_size,
            leader_display_name=event.player_name,
            connection_id=ctx.connection_id,
        )
    except ValueError as exc:
        return error_response(ctx, map_value_error_code(str(exc)), str(exc))

    return snapshot_response(ctx, state, viewer_player_id=str(state.player.id))
