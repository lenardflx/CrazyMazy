from __future__ import annotations

from shared.events import ClientJoinRoomEvent, parse_event
from shared.protocol import make_message


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
    assert parse_event(make_message("server.snapshot")) is None


def test_parse_event_returns_none_for_invalid_join_payload() -> None:
    assert parse_event(
        make_message(ClientJoinRoomEvent.message_type, {"room_id": "ROOM-1"})
    ) is None
