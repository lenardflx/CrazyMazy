# Author: Lenard Felix, Raphael Eiden
from __future__ import annotations

"""
This file focuses on the two main types of responses the server can 
send to a client request (client events such as `ClientJoinGameEvent`). 

The server can either detect invalid packet content such as an invalid move, 
trying to join a non-existent game etc. or validate the move and actually update 
the current board. Latter response is made using the `ServerGameSnapshotEvent` 
which sends the current state of the game to a client, while errors are 
sent via the `ServerResponseErrorEvent`. 

The event handlers on the server-side have `OutgoingMessage` as return type 
which is why this helper file exists to construct these objects from the 
corresponding events. 
"""

from server.network.connections import get_connection
from server.network.models import OutgoingMessage, RequestContext
from shared.events import ServerGameSnapshotEvent, ServerResponseErrorEvent, ServerGameLeftEvent
from shared.lib.snapshot import make_game_snapshot_payload
from shared.protocol import ErrorCode
from shared.game.state import GameState


def error_response(ctx: RequestContext, code: ErrorCode) -> list[OutgoingMessage]:
    """
    This function creates an `OutgoingMessage` object which contains a
    `ServerResponseErrorEvent`. This can be used in client event handler methods
    to respond to specific events with an error message.

    This function is commonly used in the service classes such as `GameService`
    whose methods are called from client event handlers.

    :param ctx:     The client connection context to build the event for.
    :param code:    The error code to encode into the error event packet.
    :return:        The `OutgoingMessage` object which can be sent in the message channel.
    """
    event = ServerResponseErrorEvent(error_code=code)
    return [OutgoingMessage(conn=ctx.conn, msg=event.to_message())]


def snapshot_response(state: GameState) -> list[OutgoingMessage]:
    """
    Builds an `OutgoingMessage` object which sends a `ServerGameSnapshotEvent`
    based on the given `GameState`. This method simply takes the content of the
    game state, converts it into a game snapshot, wraps into an event and
    then wraps the event into an outgoing message object.

    :param state:   The game state to build the snapshot from.
    :return:        The outgoing message object containing the event.
    """
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
