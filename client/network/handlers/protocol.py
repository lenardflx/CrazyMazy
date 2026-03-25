# Author: Lenard Felix

from __future__ import annotations

from client.network.dispatch import dispatcher
from client.network.state import ClientState
from shared.events import ServerGameSnapshotEvent, ServerResponseErrorEvent


@dispatcher.handler(ServerResponseErrorEvent)
def handle_response_error(state: ClientState, event: ServerResponseErrorEvent) -> None:
    state.last_error = {
        "code": event.code,
        "message": event.message,
    }


@dispatcher.handler(ServerGameSnapshotEvent)
def handle_game_snapshot(state: ClientState, event: ServerGameSnapshotEvent) -> None:
    state.game_snapshot = event.payload
