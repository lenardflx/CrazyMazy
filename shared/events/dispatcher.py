# Author: Lenard Felix

from __future__ import annotations

import logging
from typing import Callable, Generic, TypeVar, cast

from shared.events.event import Event

TContext = TypeVar("TContext")
TReturn = TypeVar("TReturn")
TEvent = TypeVar("TEvent", bound=Event)

logger = logging.getLogger(__name__)


class EventDispatcher(Generic[TContext, TReturn]):
    """Dispatch typed events to their handlers."""

    def __init__(self) -> None:
        self._handlers: dict[type[Event], Callable[[TContext, Event], TReturn]] = {}

    def handler(
        self,
        event_type: type[TEvent],
    ) -> Callable[[Callable[[TContext, TEvent], TReturn]], Callable[[TContext, TEvent], TReturn]]:
        """Register the handler for one concrete event class."""
        def decorator(
            fn: Callable[[TContext, TEvent], TReturn],
        ) -> Callable[[TContext, TEvent], TReturn]:
            if event_type in self._handlers:
                raise ValueError(f"Handler already registered for event type: {event_type.__name__}")
            self._handlers[event_type] = cast(Callable[[TContext, Event], TReturn], fn)
            return fn

        return decorator

    def dispatch(self, ctx: TContext, event: Event) -> TReturn | None:
        """Dispatch one parsed event to its registered handler."""
        fn = self._handlers.get(type(event))
        if fn is None:
            logger.warning("Unhandled event type: %s", type(event).__name__)
            return None
        return fn(ctx, event)
