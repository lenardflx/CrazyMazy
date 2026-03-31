# Author: Lenard Felix

"""
This file defines the color palette and font settings for the client UI.
The color palette is defined as a set of named RGB tuples, which can be used throughout the UI to have consistent style.
"""

from __future__ import annotations

import pygame as pg

Color = tuple[int, int, int]

# Background
BACKGROUND: Color = (147, 197, 209)
PANEL: Color = (246, 220, 171)
PANEL_ALT: Color = (214, 156, 89)
PANEL_SHADOW: Color = (110, 72, 41)

# Text
TEXT_PRIMARY: Color = (70, 43, 24)
TEXT_MUTED: Color = (120, 83, 49)

# Accent (orange-gold family)
ACCENT: Color = (230, 132, 41)
ACCENT_DARK: Color = (145, 82, 34)
ACCENT_SOFT: Color = (247, 182, 94)

# State colors
DISABLED: Color = (163, 134, 98)
ACTIVE_OUTLINE: Color = (255, 205, 92)
MOVE_HIGHLIGHT: Color = (122, 176, 108)
ERROR: Color = (176, 68, 48)

# Pixel-art panel defaults
PIXEL_CUT = 7
PIXEL_BORDER = 3
PIXEL_SHADOW_OFFSET = 3


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


def render_text(font_obj: pg.font.Font, text: str, color: Color) -> pg.Surface:
    """Render UI text without anti-aliasing so it reads closer to pixel art."""
    return font_obj.render(text, False, color)


def _pixel_cut(rect: pg.Rect) -> int:
    return max(2, min(PIXEL_CUT, rect.width // 4, rect.height // 4))


def _pixel_fill(surface: pg.Surface, rect: pg.Rect, color: Color, *, cut: int | None = None) -> None:
    """Fill a stepped cut-corner rectangle row-by-row so larger cuts stay stable."""
    if rect.width <= 0 or rect.height <= 0:
        return

    resolved_cut = _pixel_cut(rect) if cut is None else max(0, min(cut, rect.width // 2, rect.height // 2))
    if resolved_cut == 0:
        pg.draw.rect(surface, color, rect)
        return

    for y in range(rect.height):
        top_inset = max(0, resolved_cut - y - 1)
        bottom_inset = max(0, resolved_cut - (rect.height - y - 1) - 1)
        inset = max(top_inset, bottom_inset)
        row_width = rect.width - inset * 2
        if row_width <= 0:
            continue
        pg.draw.line(
            surface,
            color,
            (rect.x + inset, rect.y + y),
            (rect.x + inset + row_width - 1, rect.y + y),
        )


def draw_pixel_rect(
    surface: pg.Surface,
    rect: pg.Rect,
    fill: Color,
    *,
    border: Color,
    shadow: Color | None = None,
) -> None:
    """Draw a filled rectangle with fixed cut-corner pixel borders."""
    if rect.width <= 0 or rect.height <= 0:
        return

    border_width = min(PIXEL_BORDER, max(1, min(rect.width, rect.height) // 6))
    cut = _pixel_cut(rect)

    if shadow is not None:
        _pixel_fill(surface, rect.move(0, PIXEL_SHADOW_OFFSET), shadow, cut=cut)

    _pixel_fill(surface, rect, border, cut=cut)

    inner = rect.inflate(-border_width * 2, -border_width * 2)
    inner_cut = max(0, cut - border_width)
    if inner.width > 0 and inner.height > 0:
        _pixel_fill(surface, inner, fill, cut=inner_cut)


_FONT_PATH = "assets/fonts/editundo.ttf"
_TITLE_FONT_PATH = "assets/fonts/ka1.ttf"


def font(size: int) -> pg.font.Font:
    """UI font (editundo) — use for all text except the main menu title."""
    return pg.font.Font(_FONT_PATH, size)


def title_font(size: int) -> pg.font.Font:
    """Display font (ka1) — use only for the main menu title."""
    return pg.font.Font(_TITLE_FONT_PATH, size)
