from __future__ import annotations

import pytest

from shared.dispatch import Dispatcher
from shared.protocol import Message, make_message


def test_dispatcher_rejects_duplicate_handlers() -> None:
    dispatcher: Dispatcher[str, int] = Dispatcher()

    @dispatcher.handler("server.snapshot")
    def first_handler(ctx: str, msg: Message) -> int:
        return len(ctx) + len(msg["type"])

    assert first_handler("x", make_message("server.snapshot")) > 0

    with pytest.raises(ValueError, match="Handler already registered"):

        @dispatcher.handler("server.snapshot")
        def second_handler(ctx: str, msg: Message) -> int:
            return 0


def test_dispatcher_passes_context_and_message_to_handler() -> None:
    dispatcher: Dispatcher[str, str] = Dispatcher()

    @dispatcher.handler("server.snapshot")
    def handle(ctx: str, msg: Message) -> str:
        return f"{ctx}:{msg['id']}:{msg['type']}"

    msg = make_message("server.snapshot")

    assert dispatcher.dispatch("ctx", msg) == f"ctx:{msg['id']}:server.snapshot"


def test_dispatcher_returns_none_for_unknown_message_type() -> None:
    dispatcher: Dispatcher[str, str] = Dispatcher()

    assert dispatcher.dispatch("ctx", make_message("server.response.error")) is None
