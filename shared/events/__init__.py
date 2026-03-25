# Author: Lenard Felix

from shared.events.dispatcher import EventDispatcher
from shared.events.error import ServerResponseErrorEvent
from shared.events.event import Event
from shared.events.game import (
    ClientGameEndTurnEvent,
    ClientGameGiveUpEvent,
    ClientGameMovePlayerEvent,
    ClientGameShiftTileEvent,
    ClientGameStartEvent,
    ServerGameFinishedEvent,
    ServerGamePlayerMovedEvent,
    ServerGameStartedEvent,
    ServerGameTileShiftedEvent,
    ServerGameTurnChangedEvent,
)
from shared.events.room import (
    ClientJoinRoomEvent,
    ServerRoomSnapshotEvent,
)
from shared.protocol import Message

EVENT_TYPES: dict[str, type[Event]] = {
    ClientJoinRoomEvent.message_type: ClientJoinRoomEvent,
    ClientGameStartEvent.message_type: ClientGameStartEvent,
    ClientGameShiftTileEvent.message_type: ClientGameShiftTileEvent,
    ClientGameMovePlayerEvent.message_type: ClientGameMovePlayerEvent,
    ClientGameEndTurnEvent.message_type: ClientGameEndTurnEvent,
    ClientGameGiveUpEvent.message_type: ClientGameGiveUpEvent,
    ServerRoomSnapshotEvent.message_type: ServerRoomSnapshotEvent,
    ServerResponseErrorEvent.message_type: ServerResponseErrorEvent,
    ServerGameStartedEvent.message_type: ServerGameStartedEvent,
    ServerGameTileShiftedEvent.message_type: ServerGameTileShiftedEvent,
    ServerGamePlayerMovedEvent.message_type: ServerGamePlayerMovedEvent,
    ServerGameTurnChangedEvent.message_type: ServerGameTurnChangedEvent,
    ServerGameFinishedEvent.message_type: ServerGameFinishedEvent,
}


def parse_event(msg: Message) -> Event | None:
    """Parse a wire message into the registered typed event for its message type."""
    event_type = EVENT_TYPES.get(msg["type"])
    if event_type is None:
        return None
    return event_type.from_message(msg)

__all__ = [
    "ClientGameEndTurnEvent",
    "ClientGameGiveUpEvent",
    "ClientGameMovePlayerEvent",
    "ClientGameShiftTileEvent",
    "ClientGameStartEvent",
    "ClientJoinRoomEvent",
    "Event",
    "EventDispatcher",
    "ServerGameFinishedEvent",
    "ServerGamePlayerMovedEvent",
    "ServerGameStartedEvent",
    "ServerGameTileShiftedEvent",
    "ServerGameTurnChangedEvent",
    "ServerResponseErrorEvent",
    "ServerRoomSnapshotEvent",
    "parse_event",
]
