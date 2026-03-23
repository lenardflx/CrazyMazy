# Author: Lenard Felix

from __future__ import annotations

import logging
from typing import Callable, Generic, TypeVar

from shared.protocol import Message

TContext = TypeVar("TContext")


class Dispatcher(Generic[TContext]):
    """Generic event dispatcher"""
    
    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[TContext, Message], None]] = {}

    def handler(self, event_type: str) -> Callable:
        """Decorator that registers a function as the handler for an event type."""
        def decorator(fn: Callable[[TContext, Message], None]) -> Callable[[TContext, Message], None]:
            self._handlers[event_type] = fn
            return fn
        return decorator

    def dispatch(self, ctx: TContext, raw: dict) -> None:
        """Call the handler based on the event type, if it exists."""
        event_type = raw.get("type")
        if not isinstance(event_type, str):
            logging.warning("invalid event type: %r", event_type)
            return
        fn = self._handlers.get(event_type)
        if fn is None:
            logging.warning("unhandled event: %s", event_type)
            return
        fn(ctx, Message.from_dict(raw))