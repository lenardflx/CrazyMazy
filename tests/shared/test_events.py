from __future__ import annotations

from shared.events import ClientJoinRoomEvent, ServerResponseErrorEvent, ServerRoomSnapshotEvent, parse_event
from shared.protocol import make_message


def test_event_to_message_uses_event_id_and_payload() -> None:
    event = ClientJoinRoomEvent(
        message_id="msg_custom",
        room_id="ROOM-1",
        player_name="Ada",
    )

    msg = event.to_message()

    assert msg["id"] == "msg_custom"
    assert msg["type"] == ClientJoinRoomEvent.message_type
    assert msg["payload"] == {
        "room_id": "ROOM-1",
        "player_name": "Ada",
    }


def test_event_generates_message_id_by_default() -> None:
    event = ClientJoinRoomEvent(
        room_id="ROOM-1",
        player_name="Ada",
    )

    assert event.message_id.startswith("msg_")


def test_parse_event_returns_join_event_for_valid_message() -> None:
    event = parse_event(
        make_message(
            ClientJoinRoomEvent.message_type,
            {"room_id": " ROOM-1 ", "player_name": " Ada "},
        )
    )

    assert isinstance(event, ClientJoinRoomEvent)
    assert event.room_id == "ROOM-1"
    assert event.player_name == "Ada"


def test_parse_event_returns_none_for_unknown_message_type() -> None:
    assert parse_event(make_message("unknown.event")) is None


def test_parse_event_returns_none_for_invalid_join_payload() -> None:
    assert parse_event(
        make_message(ClientJoinRoomEvent.message_type, {"room_id": "ROOM-1"})
    ) is None


def test_parse_event_returns_snapshot_event_for_snapshot_message() -> None:
    event = parse_event(make_message(ServerRoomSnapshotEvent.message_type, {"room_id": "ROOM-1"}))

    assert isinstance(event, ServerRoomSnapshotEvent)
    assert event.payload == {"room_id": "ROOM-1"}


def test_parse_event_returns_error_event_for_error_message() -> None:
    event = parse_event(
        make_message(
            ServerResponseErrorEvent.message_type,
            {"code": "ROOM_NOT_FOUND", "message": "missing"},
        )
    )

    assert isinstance(event, ServerResponseErrorEvent)
    assert event.code == "ROOM_NOT_FOUND"
    assert event.message == "missing"
