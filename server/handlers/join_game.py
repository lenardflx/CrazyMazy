# Author: Lenard Felix

from __future__ import annotations

from server.network.dispatch import dispatcher
from server.network.models import OutgoingMessage, RequestContext
from shared.events import ClientJoinGameEvent


@dispatcher.handler(ClientJoinGameEvent)
def handle_join_game(ctx: RequestContext, event: ClientJoinGameEvent) -> list[OutgoingMessage]:
    print(
        f"[server] join-game request from {ctx.addr}: "
        f"player={event.player_name!r} game={event.game_id!r}"
    )
    return []
