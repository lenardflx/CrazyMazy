# Author: Lenard Felix, Raphael Eiden

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Self

from shared.events.event import Event
from shared.protocol import Message, ErrorCode


@dataclass(frozen=True)
class ServerResponseErrorEvent(Event):
    """Server error response."""

    message_type = "response.error"

    error_code: ErrorCode

    def to_payload(self) -> Mapping[str, Any]:
        return {
            "error_code": self.error_code,
        }

    @classmethod
    def from_message(cls, msg: Message) -> Self | None:
        payload = msg["payload"]
        if payload is None:
            return None
        try:
            code: ErrorCode = ErrorCode(payload["error_code"])
        except KeyError:
            return None
        return cls(
            message_id=msg["id"],
            error_code=code,
        )
