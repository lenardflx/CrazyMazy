# Author: Lenard Felix, Raphael Eiden
from __future__ import annotations
"""
This file handles all incoming events from the server.
The handler methods update the global `ClientState`, which can then be
used by the MainLoop and Screen-Manager to update the actually displayed
content.
"""

"""
Protocol event handlers for incoming server messages.
Each handler is registered with the dispatcher and is called when the corresponding event type arrives.
Handlers update the ClientState's version counters so that the TransportSync can detect changes on the next frame.
"""

from client.network.dispatch import dispatcher
from client.network.state import ClientState
from shared.events import ServerGameLeftEvent, ServerGameSnapshotEvent, ServerResponseErrorEvent


@dispatcher.handler(ServerResponseErrorEvent)
def handle_response_error(state: ClientState, event: ServerResponseErrorEvent) -> None:
    state.last_error = event.error_code
    state.error_version += 1


@dispatcher.handler(ServerGameSnapshotEvent)
def handle_game_snapshot(state: ClientState, event: ServerGameSnapshotEvent) -> None:
    """Store the latest game snapshot and bump the version so TransportSync picks it up."""
    state.game_snapshot = event.payload
    state.snapshot_version += 1


# NOTE: Raphael's changes should make this deprecated.
@dispatcher.handler(ServerGameLeftEvent)
def handle_game_left(state: ClientState, event: ServerGameLeftEvent) -> None:
    """Store the game-left payload and bump the version so TransportSync can trigger a scene transition."""
    state.game_left = event.payload
    state.game_left_version += 1
