# Author: Lenard Felix
 
from __future__ import annotations

from server.network.connections import get_connection
from server.network.models import OutgoingMessage, RequestContext
from shared.events import ServerGameLeftEvent, ServerGameSnapshotEvent, ServerResponseErrorEvent
from shared.lib.snapshot import make_game_snapshot_payload
from shared.protocol import ErrorCode
from shared.game.state import GameState


def error_response(ctx: RequestContext, code: str, message: str) -> list[OutgoingMessage]:
    event = ServerResponseErrorEvent(code=code, message=message)
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


# TODO: this is a temp mapping function and should be replaced by proper exception handling and error types
def map_value_error_code(error_message: str) -> str:
    normalized = error_message.lower()
    if "display name already taken" in normalized:
        return ErrorCode.DISPLAY_NAME_TAKEN
    if "invalid board size" in normalized:
        return ErrorCode.INVALID_BOARD_SIZE
    if "not joinable" in normalized:
        return ErrorCode.GAME_NOT_JOINABLE
    if "invalid display name" in normalized:
        return ErrorCode.INVALID_PAYLOAD
    return ErrorCode.INVALID_PAYLOAD
