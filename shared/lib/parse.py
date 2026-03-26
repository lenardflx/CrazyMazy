# Author: Lenard Felix

from __future__ import annotations

from enum import StrEnum
from typing import Any


def parse_str(value: Any) -> str | None:
    """Return ``value`` if it is a non-empty string, otherwise ``None``."""
    return value if isinstance(value, str) and value else None


def parse_optional_str(value: Any) -> str | None:
    """Return ``value`` as a string, or ``None`` if absent or invalid."""
    if value is None:
        return None
    return parse_str(value)


def parse_enum(value: Any, enum_type: type[StrEnum]) -> str | None:
    """Return ``value`` if it is a valid member of ``enum_type``, otherwise ``None``."""
    if not isinstance(value, str):
        return None
    try:
        enum_type(value)
    except ValueError:
        return None
    return value


def parse_optional_enum(value: Any, enum_type: type[StrEnum]) -> str | None:
    """Return ``value`` as a valid enum string, or ``None`` if absent or invalid."""
    if value is None:
        return None
    return parse_enum(value, enum_type)


def parse_int(value: Any) -> int | None:
    """Return ``value`` if it is a plain integer (not a bool), otherwise ``None``."""
    if not isinstance(value, int) or isinstance(value, bool):
        return None
    return value


def parse_optional_int(value: Any) -> int | None:
    """Return ``value`` as an integer, or ``None`` if absent or invalid."""
    if value is None:
        return None
    return parse_int(value)


def parse_bool(value: Any) -> bool | None:
    """Return ``value`` if it is a bool, otherwise ``None``."""
    if not isinstance(value, bool):
        return None
    return value
