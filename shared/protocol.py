# Author: Lenard Felix, Raphael Eiden

from __future__ import annotations

from typing import Any, Mapping, NotRequired, TypedDict, cast

from shared.utils.ids import new_message_id


class ErrorCode:
    """

    """
    INVALID_MESSAGE = "INVALID_MESSAGE"
    INVALID_PAYLOAD = "INVALID_PAYLOAD"

    GAME_NOT_FOUND = "GAME_NOT_FOUND"
    GAME_FULL = "GAME_FULL"
    INVALID_BOARD_SIZE = "INVALID_BOARD_SIZE"
    DISPLAY_NAME_TAKEN = "DISPLAY_NAME_TAKEN"
    GAME_NOT_JOINABLE = "GAME_NOT_JOINABLE"


class Message(TypedDict):
    """
    A message is the exchange medium used in the packet channel.
    When an event is triggered (either by the server or the client)
    a new instance of the respective event class (e.g. ClientConnectLobbyEvent)
    is created.

    To be able to send this event through the socket connection, we need to
    convert it into a simple string that we can easily parse back to an event
    on the other side.

    Messages in the socket channel are separated by lines (`"\n"`).
    So, when reading received data, you can scan for new lines to distinguish
    between different messages.

    Attributes:
        id:         The unique id of the message. This will be used to send
                    replies
        type:       The event type this message originates from (usually the class name
                    of the event and specified in the respective event class)
        payload:    The attributes that have to be carried by the event
                    such as "game id" for client connect lobby event.
        reply_to:   The messages to be sent back as a response.
    """
    id: str
    type: str
    payload: Mapping[str, Any]
    reply_to: NotRequired[str]


def make_message(msg_type: str, payload: Mapping[str, Any] | None = None) -> Message:
    """
    Generates a new message object with the given type and payload.
    A random message id is automatically generated.

    :param msg_type: The type of the message.
    :param payload:  The message payload.
    :return: The message object carrying the respective data and a random id.
    """
    return {
        "id": new_message_id(),
        "type": msg_type,
        "payload": payload or {},
    }


def parse_message(raw: object) -> Message | None:
    """
    Checks if the given object fulfills the criteria of a Message by checking
    whether all attributes (id, type, payload, reply_to) are present.
    If so, the object is cast to a Message object. Otherwise, None will be returned.

    :param raw: The raw object to be checked and converted.
    :return:    The message object cast from the raw object or `None` if no
                Message object could be constructed.
    """
    # check if raw is a general dict (Message is a typed dict)
    if not isinstance(raw, dict):
        return None
    if not (
        isinstance(raw.get("id"), str)
        and isinstance(raw.get("type"), str)
        and isinstance(raw.get("payload"), dict)
    ):
        return None
    # "reply_to" is not mandatory for a message object, but has to be a string
    if "reply_to" in raw and not isinstance(raw["reply_to"], str):
        return None
    # as Message is a typed dict, we can perform a direct cast
    return cast(Message, raw)
