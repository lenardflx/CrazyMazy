# Author: Lenard Felix
 
# Author: Lenard Felix, Raphael Eiden
from __future__ import annotations

from server.network.connections import get_connection
from server.network.models import OutgoingMessage, RequestContext
from server.service import GameState
from shared.events import ServerGameLeftEvent, ServerGameSnapshotEvent, ServerResponseErrorEvent
from shared.lib.snapshot import make_game_snapshot_payload
from shared.protocol import ErrorCode


def error_response(ctx: RequestContext, code: ErrorCode) -> list[OutgoingMessage]:
    event = ServerResponseErrorEvent(error_code=code)
    return [OutgoingMessage(conn=ctx.conn, msg=event.to_message())]


def snapshot_response(state: GameState) -> list[OutgoingMessage]:
    outgoing: list[OutgoingMessage] = []
    for player in state.players:
        if player.connection_id is None:
            continue
        conn = get_connection(player.connection_id)
        if conn is None:
            continue
        snapshot = make_game_snapshot_payload(
            state.game,
            state.players,
            state.tiles,
            state.treasures_by_player,
            viewer_player_id=str(player.id),
        )
        outgoing.append(OutgoingMessage(conn=conn, msg=ServerGameSnapshotEvent(payload=snapshot).to_message()))
    return outgoing


def left_response(ctx: RequestContext, reason: str) -> list[OutgoingMessage]:
    event = ServerGameLeftEvent(payload={"reason": reason})
    return [OutgoingMessage(conn=ctx.conn, msg=event.to_message())]
