# Author: Lenard Felix, Raphael Eiden

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Self

from shared.events.event import Event
from shared.lib.error import parse_error_payload
from shared.protocol import Message
from shared.types.payloads import ErrorPayload


@dataclass(frozen=True)
class ServerResponseErrorEvent(Event):
    """Server error response."""

    message_type = "response.error"

    code: str
    message: str

    def to_payload(self) -> Mapping[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
        }

    @classmethod
    def from_message(cls, msg: Message) -> Self | None:
        payload: ErrorPayload | None = parse_error_payload(msg["payload"])
        if payload is None:
            return None
        return cls(
            message_id=msg["id"],
            code=payload["code"],
            message=payload["message"],
        )
