from __future__ import annotations

from server.network.models import OutgoingMessage, RequestContext
from server.service import ConnectionState, GameState
from shared.events import ServerGameSnapshotEvent, ServerResponseErrorEvent
from shared.lib.snapshot import make_game_snapshot_payload
from shared.protocol import ErrorCode


def error_response(ctx: RequestContext, code: str, message: str) -> list[OutgoingMessage]:
    event = ServerResponseErrorEvent(code=code, message=message)
    return [OutgoingMessage(conn=ctx.conn, msg=event.to_message())]


def snapshot_response(
    ctx: RequestContext,
    state: ConnectionState | GameState,
    *,
    viewer_player_id: str | None,
) -> list[OutgoingMessage]:
    players = [state.player] if isinstance(state, ConnectionState) else state.players
    game = state.game
    snapshot = make_game_snapshot_payload(game, players, viewer_player_id=viewer_player_id)
    event = ServerGameSnapshotEvent(payload=snapshot)
    # TODO: Broadcast updated snapshots to every connected game member once the server tracks sockets by connection_id.
    return [OutgoingMessage(conn=ctx.conn, msg=event.to_message())]


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
