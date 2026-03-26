# Author: Lenard Felix

from __future__ import annotations

from shared.protocol import make_message, parse_message


def test_make_message_sets_id_type_and_default_payload() -> None:
    msg = make_message("server.snapshot")

    assert msg["id"].startswith("msg_")
    assert msg["type"] == "server.snapshot"
    assert msg["payload"] == {}


def test_make_message_preserves_payload() -> None:
    msg = make_message("server.response.error", {"code": "INVALID_MESSAGE"})

    assert msg["payload"] == {"code": "INVALID_MESSAGE"}


def test_parse_message_returns_none_for_missing_type() -> None:
    assert parse_message({"id": "msg_1", "payload": {}}) is None


def test_parse_message_returns_none_for_non_string_type() -> None:
    assert parse_message({"id": "msg_1", "type": 123, "payload": {}}) is None


def test_parse_message_returns_message_for_valid_input() -> None:
    raw = {
        "id": "msg_1",
        "type": "server.snapshot",
        "payload": {},
        "reply_to": "msg_0",
    }

    assert parse_message(raw) == raw
