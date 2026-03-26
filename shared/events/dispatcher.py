# Author: Lenard Felix, Raphael Eiden

from __future__ import annotations

import logging
from typing import Callable, Generic, TypeVar, cast

from shared.events.event import Event

TContext = TypeVar("TContext")
"""
Generic type for event context. The context is used by the
dispatcher to transfer information about the client connection.
Client and Server can define custom classes for the context
which is why we use this generic type parameter.
"""

TReturn = TypeVar("TReturn")
"""The generic return type of a handler method."""

TEvent = TypeVar("TEvent", bound=Event)
"""Generic type for any event class (classes that inherit from the Event base class)"""

logger = logging.getLogger(__name__)


class EventDispatcher(Generic[TContext, TReturn]):
    """
    Generic event dispatcher for client and server.
    Both client and server can define custom classes for the context and return types
    and initialize a dispatcher with these parameters. The dispatcher can then be used
    to trigger events

    Type Parameters:
        TContext:   The context each handler method receives.
        TReturn:    The return type each handler method has to have.
    """

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
            logger.info(f"Registered handler for event type: {event_type.__name__}")
            return fn

        return decorator

    def dispatch(self, ctx: TContext, event: Event) -> TReturn | None:
        """
        Calls the handler function associated with the given event (type).

        :param ctx:     The context with which the event is triggered.
        :param event:   The event to trigger. The information contained in the event
                        instance is passed to the handler method.
        :return: If the handler decides to send a response, it will be returned as `TReturn`.
        """
        fn = self._handlers.get(type(event))
        if fn is None:
            logger.warning("Unhandled event type: %s", type(event).__name__)
            return None
        return fn(ctx, event)
