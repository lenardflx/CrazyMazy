# Author: Lenard Felix, Raphael Eiden

from __future__ import annotations

from enum import StrEnum
from typing import Any, Mapping, NotRequired, TypedDict, cast

from shared.utils.ids import new_message_id

class ErrorCode(StrEnum):
    CONNECTION_ERROR = "CONNECTION_ERROR"
    INVALID_MESSAGE = "INVALID_MESSAGE"
    INVALID_PAYLOAD = "INVALID_PAYLOAD"

    DISPLAY_NAME_NOT_ENTERED = "DISPLAY_NAME_NOT_ENTERED"
    DISPLAY_NAME_TAKEN = "DISPLAY_NAME_TAKEN"
    DISPLAY_NAME_TOO_SHORT = "DISPLAY_NAME_TOO_SHORT"
    DISPLAY_NAME_TOO_LONG = "DISPLAY_NAME_TOO_LONG"
    DISPLAY_NAME_ILLEGAL = "DISPLAY_NAME_ILLEGAL"

    JOIN_CODE_NOT_ENTERED = "JOIN_CODE_NOT_ENTERED"
    INVALID_PLAYER_LIMIT = "INVALID_PLAYER_LIMIT"
    NO_PUBLIC_LOBBY = "NO_PUBLIC_LOBBY"

    INVALID_BOARD_SIZE = "INVALID_BOARD_SIZE"
    """
    The board size (board width) is invalid, as it is either 
    too big/small or an even number. 
    """

    INVALID_INSERTION_INDEX = "INVALID_INSERTION_INDEX"
    """
    A tile cannot be inserted at this position because 
    the tile at this index is a fixed tile. 
    """

    TILE_INSERTION_BLOCKED = "TILE_INSERTION_BLOCKED"
    """
    When a player inserts a tile, the next player cannot undo their 
    move by simply inserting the tile back into the same position, so 
    the insertion is blocked at that specific index.
    """

    GAME_NOT_FOUND = "GAME_NOT_FOUND"
    GAME_FULL = "GAME_FULL"
    GAME_NOT_JOINABLE = "GAME_NOT_JOINABLE"

    GAME_INACTIVE = "GAME_INACTIVE"
    """
    The game is expected to be in the game phase, but currently 
    is in another phase such as PRE- or POSTGAME. 
    """

    GAME_NOT_STARTABLE = "GAME_NOT_STARTABLE"
    """
    The game cannot be started right now, for example due to an 
    incorrect game phase (e.g. `POST_GAME`)
    """

    PLAYER_COUNT_INSUFFICIENT = "PLAYER_COUNT_INSUFFICIENT"
    """
    There are not enough players to perform an action, such as 
    the minimum player count is not fulfilled when attempting to start the game.
    """

    PLAYER_INSUFFICIENT_PERMISSION = "PLAYER_INSUFFICIENT_PERMISSION"
    """
    When a player lacks permission to perform an action, such 
    as attempting to start a game despite not being the leader. 
    """

    PLAYER_HAS_NO_POSITION = "PLAYER_HAS_NO_POSITION"
    """
    When a player wants to move and there is no start position 
    known to validate that move, this error is thrown. 
    """

    PLAYER_NO_TURN = "PLAYER_NO_TURN"
    """
    The player has sent any move packet (shift or move) but its
    actually not their turn.
    """

    UNEXPECTED_TURN_PHASE = "UNEXPECTED_TURN_PHASE"
    """
    Each turn consists of two actions:
    1) Insert and shift a tile 
    2) Move to another tile 
    If the player sends a move packet, although they should actually 
    insert a tile (or the other way round) this error is thrown.
    """

    TARGET_POSITION_UNREACHABLE = "TARGET_POSITION_UNREACHABLE"
    """
    When a player wants to move from one tile to another, but there is no valid 
    path between these tiles, the server refuses the move with this error. 
    """

    PLAYER_NOT_FOUND = "PLAYER_NOT_FOUND"
    """
    When a player is not found, i.e. there is no player with a 
    given id or the connection does not exist.
    """

    ADD_NPC_ONLY_IN_LOBBY = "ADD_NPC_ONLY_IN_LOBBY"
    """
    When a client sends an NPC create packet but the game is not in 
    lobby state, so no players/NPCs can join. 
    """

class DisplayMessage(StrEnum):
    SERVER_NOT_REACHABLE = "SERVER_NOT_REACHABLE"
    UNKNOWN_MESSAGE_TYPE = "UNKNOWN_MESSAGE_TYPE"


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
