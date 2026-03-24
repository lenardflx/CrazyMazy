# Author: Lenard Felix

from shared.events.dispatcher import EventDispatcher
from shared.events.event import ClientJoinRoomEvent, Event
from shared.protocol import Message

EVENT_TYPES: dict[str, type[Event]] = {
    ClientJoinRoomEvent.message_type: ClientJoinRoomEvent,
}


def parse_event(msg: Message) -> Event | None:
    event_type = EVENT_TYPES.get(msg["type"])
    if event_type is None:
        return None
    return event_type.from_message(msg)

__all__ = ["ClientJoinRoomEvent", "Event", "EventDispatcher", "parse_event"]
