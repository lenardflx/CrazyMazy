from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar
import pytest

from shared.events import Event, EventDispatcher
from shared.protocol import Message


@dataclass(frozen=True)
class SnapshotEvent(Event):
    message_type: ClassVar[str] = "test.snapshot"
    label: str

    @classmethod
    def from_message(cls, msg: Message) -> "SnapshotEvent | None":
        return cls(message_id=msg["id"], label="snapshot")


@dataclass(frozen=True)
class ErrorEvent(Event):
    message_type: ClassVar[str] = "test.error"
    code: str

    @classmethod
    def from_message(cls, msg: Message) -> "ErrorEvent | None":
        return cls(message_id=msg["id"], code="INVALID")


def test_dispatcher_rejects_duplicate_handlers() -> None:
    dispatcher: EventDispatcher[str, int] = EventDispatcher()

    @dispatcher.handler(SnapshotEvent)
    def first_handler(ctx: str, event: SnapshotEvent) -> int:
        return len(ctx) + len(event.label)

    assert first_handler("x", SnapshotEvent(message_id="msg_1", label="snapshot")) > 0

    with pytest.raises(ValueError, match="Handler already registered"):

        @dispatcher.handler(SnapshotEvent)
        def second_handler(ctx: str, event: SnapshotEvent) -> int:
            return 0


def test_dispatcher_passes_context_and_message_to_handler() -> None:
    dispatcher: EventDispatcher[str, str] = EventDispatcher()

    @dispatcher.handler(SnapshotEvent)
    def handle(ctx: str, event: SnapshotEvent) -> str:
        return f"{ctx}:{event.message_id}:{event.label}"

    event = SnapshotEvent(message_id="msg_1", label="snapshot")

    assert dispatcher.dispatch("ctx", event) == "ctx:msg_1:snapshot"


def test_dispatcher_returns_none_for_unknown_message_type() -> None:
    dispatcher: EventDispatcher[str, str] = EventDispatcher()

    assert dispatcher.dispatch("ctx", ErrorEvent(message_id="msg_2", code="INVALID")) is None
