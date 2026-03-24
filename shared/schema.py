# Author: Lenard Felix

from __future__ import annotations

from typing import Any, TypedDict


class ErrorPayload(TypedDict):
    code: str
    message: str


def parse_error_payload(payload: dict[str, Any]) -> ErrorPayload | None:
    code = payload.get("code")
    message = payload.get("message")
    if not isinstance(code, str) or not isinstance(message, str):
        return None
    return {"code": code, "message": message}
