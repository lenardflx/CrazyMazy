# Author: Lenard Felix

from shared.events.dispatcher import EventDispatcher
from shared.events.event import (
    ClientJoinRoomEvent,
    Event,
    ServerResponseErrorEvent,
    ServerRoomSnapshotEvent,
)
from shared.protocol import Message

EVENT_TYPES: dict[str, type[Event]] = {
    ClientJoinRoomEvent.message_type: ClientJoinRoomEvent,
    ServerRoomSnapshotEvent.message_type: ServerRoomSnapshotEvent,
    ServerResponseErrorEvent.message_type: ServerResponseErrorEvent,
}


def parse_event(msg: Message) -> Event | None:
    """Parse a wire message into the registered typed event for its message type."""
    event_type = EVENT_TYPES.get(msg["type"])
    if event_type is None:
        return None
    return event_type.from_message(msg)

__all__ = [
    "ClientJoinRoomEvent",
    "Event",
    "EventDispatcher",
    "ServerResponseErrorEvent",
    "ServerRoomSnapshotEvent",
    "parse_event",
]
