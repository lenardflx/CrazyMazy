# Author: Lenard Felix

from shared.events.dispatcher import EventDispatcher
from shared.events.error import ServerResponseErrorEvent
from shared.events.event import Event
from shared.events.game import (
    ClientCreateLobbyEvent,
    ClientGameAddNpcEvent,
    ClientGameEndTurnEvent,
    ClientGameGiveUpEvent,
    ClientGameLeaveEvent,
    ClientJoinGameEvent,
    ClientGameMovePlayerEvent,
    ClientGameShiftTileEvent,
    ClientGameStartEvent,
    ServerGameFinishedEvent,
    ServerGameLeftEvent,
    ServerGamePlayerMovedEvent,
    ServerGameSnapshotEvent,
    ServerGameStartedEvent,
    ServerGameTileShiftedEvent,
    ServerGameTurnChangedEvent,
)
from shared.protocol import Message

EVENT_TYPES: dict[str, type[Event]] = {
    ClientCreateLobbyEvent.message_type: ClientCreateLobbyEvent,
    ClientJoinGameEvent.message_type: ClientJoinGameEvent,
    ClientGameStartEvent.message_type: ClientGameStartEvent,
    ClientGameAddNpcEvent.message_type: ClientGameAddNpcEvent,
    ClientGameShiftTileEvent.message_type: ClientGameShiftTileEvent,
    ClientGameMovePlayerEvent.message_type: ClientGameMovePlayerEvent,
    ClientGameEndTurnEvent.message_type: ClientGameEndTurnEvent,
    ClientGameLeaveEvent.message_type: ClientGameLeaveEvent,
    ClientGameGiveUpEvent.message_type: ClientGameGiveUpEvent,
    ServerGameSnapshotEvent.message_type: ServerGameSnapshotEvent,
    ServerResponseErrorEvent.message_type: ServerResponseErrorEvent,
    ServerGameStartedEvent.message_type: ServerGameStartedEvent,
    ServerGameTileShiftedEvent.message_type: ServerGameTileShiftedEvent,
    ServerGamePlayerMovedEvent.message_type: ServerGamePlayerMovedEvent,
    ServerGameTurnChangedEvent.message_type: ServerGameTurnChangedEvent,
    ServerGameFinishedEvent.message_type: ServerGameFinishedEvent,
    ServerGameLeftEvent.message_type: ServerGameLeftEvent,
}


def parse_event(msg: Message) -> Event | None:
    """Parse a wire message into the registered typed event for its message type."""
    event_type = EVENT_TYPES.get(msg["type"])
    if event_type is None:
        return None
    return event_type.from_message(msg)

__all__ = [
    "ClientCreateLobbyEvent",
    "ClientGameAddNpcEvent",
    "ClientGameEndTurnEvent",
    "ClientGameGiveUpEvent",
    "ClientGameLeaveEvent",
    "ClientJoinGameEvent",
    "ClientGameMovePlayerEvent",
    "ClientGameShiftTileEvent",
    "ClientGameStartEvent",
    "Event",
    "EventDispatcher",
    "ServerGameFinishedEvent",
    "ServerGameLeftEvent",
    "ServerGamePlayerMovedEvent",
    "ServerGameSnapshotEvent",
    "ServerGameStartedEvent",
    "ServerGameTileShiftedEvent",
    "ServerGameTurnChangedEvent",
    "ServerResponseErrorEvent",
    "parse_event",
]
