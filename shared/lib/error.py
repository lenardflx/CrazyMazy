# Author: Lenard Felix

from __future__ import annotations

from typing import Any, Mapping

from shared.lib.parse import parse_str
from shared.schema import ErrorPayload


def parse_error_payload(payload: Mapping[str, Any]) -> ErrorPayload | None:
    code = parse_str(payload.get("code"))
    message = parse_str(payload.get("message"))
    if code is None or message is None:
        return None
    return {"code": code, "message": message}
