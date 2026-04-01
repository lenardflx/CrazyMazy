# Author: Lenard Felix, Raphael Eiden

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
    ServerGameLeftEvent,
    ServerGameSnapshotEvent, ClientKickPlayerEvent,
)
from shared.protocol import Message

EVENT_TYPES: dict[str, type[Event]] = {
    ClientCreateLobbyEvent.message_type: ClientCreateLobbyEvent,
    ClientJoinGameEvent.message_type: ClientJoinGameEvent,
    ClientKickPlayerEvent.message_type: ClientKickPlayerEvent,
    ClientGameStartEvent.message_type: ClientGameStartEvent,
    ClientGameAddNpcEvent.message_type: ClientGameAddNpcEvent,
    ClientGameShiftTileEvent.message_type: ClientGameShiftTileEvent,
    ClientGameMovePlayerEvent.message_type: ClientGameMovePlayerEvent,
    ClientGameEndTurnEvent.message_type: ClientGameEndTurnEvent,
    ClientGameLeaveEvent.message_type: ClientGameLeaveEvent,
    ClientGameGiveUpEvent.message_type: ClientGameGiveUpEvent,
    ServerGameSnapshotEvent.message_type: ServerGameSnapshotEvent,
    ServerResponseErrorEvent.message_type: ServerResponseErrorEvent,
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
    "ClientKickPlayerEvent",
    "ClientGameMovePlayerEvent",
    "ClientGameShiftTileEvent",
    "ClientGameStartEvent",
    "Event",
    "EventDispatcher",
    "ServerGameLeftEvent",
    "ServerGameSnapshotEvent",
    "ServerResponseErrorEvent",
    "parse_event",
]
