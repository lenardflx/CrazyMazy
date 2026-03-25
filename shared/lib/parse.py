# Author: Lenard Felix

from __future__ import annotations

from enum import StrEnum
from typing import Any


def parse_str(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def parse_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return parse_str(value)


def parse_enum(value: Any, enum_type: type[StrEnum]) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        enum_type(value)
    except ValueError:
        return None
    return value


def parse_optional_enum(value: Any, enum_type: type[StrEnum]) -> str | None:
    if value is None:
        return None
    return parse_enum(value, enum_type)


def parse_int(value: Any) -> int | None:
    if not isinstance(value, int) or isinstance(value, bool):
        return None
    return value


def parse_optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return parse_int(value)


def parse_bool(value: Any) -> bool | None:
    if not isinstance(value, bool):
        return None
    return value
