# Author: Lenard Felix

from __future__ import annotations

import logging
from typing import Callable, Generic, TypeVar

from shared.protocol import Message, get_message_type

TContext = TypeVar("TContext")
TReturn = TypeVar("TReturn")

logger = logging.getLogger(__name__)


class Dispatcher(Generic[TContext, TReturn]):
    """Generic message dispatcher"""

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[TContext, Message], TReturn]] = {}

    def handler(
        self,
        message_type: str,
    ) -> Callable[[Callable[[TContext, Message], TReturn]], Callable[[TContext, Message], TReturn]]:
        """Register a handler for one message type."""

        def decorator(
            fn: Callable[[TContext, Message], TReturn],
        ) -> Callable[[TContext, Message], TReturn]:
            if message_type in self._handlers:
                raise ValueError(f"Handler already registered for message type: {message_type}")
            self._handlers[message_type] = fn
            return fn

        return decorator

    def get_handler(self, msg: Message) -> Callable[[TContext, Message], TReturn] | None:
        """Resolve the registered handler for a message."""
        message_type = get_message_type(msg)
        return self._handlers.get(message_type)

    def dispatch(self, ctx: TContext, msg: Message) -> TReturn | None:
        """Dispatch a message to its registered handler."""
        fn = self.get_handler(msg)
        if fn is None:
            logger.warning("Unhandled message type: %s", get_message_type(msg))
            return None
        return fn(ctx, msg)
    
