# Author: Lenard Felix

"""
This file defines the color palette and font settings for the client UI.
The color palette is defined as a set of named RGB tuples, which can be used throughout the UI to have consistent style.
"""

from __future__ import annotations

import pygame as pg

Color = tuple[int, int, int]

BACKGROUND: Color = (76, 96, 122)
PANEL: Color = (238, 227, 208)
PANEL_SHADOW: Color = (58, 74, 97)
PANEL_ALT: Color = (216, 194, 160)
TEXT_PRIMARY: Color = (44, 31, 24)
TEXT_MUTED: Color = (98, 79, 64)
ACCENT: Color = (176, 92, 46)
ACCENT_DARK: Color = (132, 100, 80)
ACCENT_SOFT: Color = (196, 132, 91)
SUCCESS: Color = (74, 132, 94)
WARNING: Color = (187, 126, 56)
DISABLED: Color = (156, 142, 129)
GRAYED: Color = (173, 173, 173)
ACTIVE_OUTLINE: Color = (223, 161, 67)
MOVE_HIGHLIGHT: Color = (104, 177, 113)
ERROR: Color = (150, 58, 48)


def _validate_amount(amount: float) -> None:
    """Validate that an interpolation amount is within the supported range of [0.0, 1.0].

    :param amount: The interpolation factor to validate.
    :raises ValueError: If ``amount`` is outside ``[0.0, 1.0]``.
    """
    if not 0.0 <= amount <= 1.0:
        raise ValueError(f"amount must be between 0.0 and 1.0, got {amount!r}")

def mix(a: int, b: int, amount: float) -> int:
    """Return a value between ``a`` and ``b`` using linear interpolation.

    :param a: The starting value returned when ``amount`` is ``0.0``.
    :param b: The target value returned when ``amount`` is ``1.0``.
    :param amount: How far to move from ``a`` toward ``b``. Expected in ``[0.0, 1.0]``,
        where ``0.5`` gives a value about halfway between them.
    :return: The interpolated integer value.
    :raises ValueError: If ``amount`` is outside ``[0.0, 1.0]``.
    """
    _validate_amount(amount)
    return int(round(a + (b - a) * amount))


def blend_color(start: Color, end: Color, amount: float) -> Color:
    """Return a color between ``start`` and ``end``.

    Each RGB channel is interpolated separately using :func:`mix`.

    :param start: The starting RGB color returned when ``amount`` is ``0.0``.
    :param end: The target RGB color returned when ``amount`` is ``1.0``.
    :param amount: How far to move from ``start`` toward ``end``. Expected in
        ``[0.0, 1.0]``, where ``0.5`` gives a roughly half-blended color.
    :return: The blended RGB color tuple.
    :raises ValueError: If ``amount`` is outside ``[0.0, 1.0]``.
    """
    return (
        mix(start[0], end[0], amount),
        mix(start[1], end[1], amount),
        mix(start[2], end[2], amount),
    )


def font(size: int, *, bold: bool = False) -> pg.font.Font:
    """
    Helper function to create a pygame font with the given size and weight.
    When we wanna switch to a different font, we only need to change it in this function.
    """
    # TODO: replace the font
    return pg.font.SysFont("verdana", size, bold=bold)
