# Author: Lenard Felix

from __future__ import annotations

from client.network.dispatch import dispatcher
from client.network.state import ClientState
from shared.events import ServerResponseErrorEvent, ServerRoomSnapshotEvent


@dispatcher.handler(ServerResponseErrorEvent)
def handle_response_error(state: ClientState, event: ServerResponseErrorEvent) -> None:
    state.last_error = {
        "code": event.code,
        "message": event.message,
    }


@dispatcher.handler(ServerRoomSnapshotEvent)
def handle_room_snapshot(state: ClientState, event: ServerRoomSnapshotEvent) -> None:
    state.room_snapshot = event.payload
