# Author: Lenard Felix, Raphael Eiden
"""
This file handles all incoming events from the server.
The handler methods update the global `ClientState`, which can then be
used by the MainLoop and Screen-Manager to update the actually displayed
content.
"""

from __future__ import annotations

from client.network.dispatch import dispatcher
from client.network.state import ClientState
from shared.events import ServerGameLeftEvent, ServerGameSnapshotEvent, ServerResponseErrorEvent


@dispatcher.handler(ServerResponseErrorEvent)
def handle_response_error(state: ClientState, event: ServerResponseErrorEvent) -> None:
    state.last_error = event.error_code
    state.error_version += 1


@dispatcher.handler(ServerGameSnapshotEvent)
def handle_game_snapshot(state: ClientState, event: ServerGameSnapshotEvent) -> None:
    state.game_snapshot = event.payload
    state.snapshot_version += 1


@dispatcher.handler(ServerGameLeftEvent)
def handle_game_left(state: ClientState, event: ServerGameLeftEvent) -> None:
    state.game_left = event.payload
    state.game_left_version += 1
