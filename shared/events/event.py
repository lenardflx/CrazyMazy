# Author: Lenard Felix, Raphael Eiden

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar, Mapping, Self

from shared.protocol import Message, make_message
from shared.utils.ids import new_message_id


@dataclass(frozen=True, kw_only=True)
class Event(ABC):
    """Typed protocol event used by dispatchers and handlers."""

    message_type: ClassVar[str]
    """The unique identifier for the event type."""

    message_id: str = field(default_factory=new_message_id)
    """A unique identifier for the event instance."""

    @abstractmethod
    def to_payload(self) -> Mapping[str, Any]:
        """Serialize the event-specific payload for transport."""
        raise NotImplementedError

    def to_message(self) -> Message:
        """Serialize the event into the wire-level message envelope."""
        msg = make_message(self.message_type, self.to_payload())
        msg["id"] = self.message_id
        return msg

    @classmethod
    @abstractmethod
    def from_message(cls, msg: Message) -> Self | None:
        """
        Converts the given message to an event instance.
        This method will automatically return the concrete type indicated
        by the type prefix in the message.

        :param msg:  The raw message to convert.
        :return:     A concrete event instance with all the attributes
        """
        raise NotImplementedError
