# Author: Lenard Felix

from __future__ import annotations

from server.network.dispatch import dispatcher
from server.network.models import OutgoingMessage, RequestContext
from shared.events import ClientJoinRoomEvent


@dispatcher.handler(ClientJoinRoomEvent)
def handle_join_room(ctx: RequestContext, event: ClientJoinRoomEvent) -> list[OutgoingMessage]:
    print(
        f"[server] join-room request from {ctx.addr}: "
        f"player={event.player_name!r} room={event.room_id!r}"
    )
    return []
