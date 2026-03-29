# Author: Lenard Felix
 
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


def mix(a: int, b: int, amount: float) -> int:
    return int(a + (b - a) * amount)


def blend_color(start: Color, end: Color, amount: float) -> Color:
    return (
        mix(start[0], end[0], amount),
        mix(start[1], end[1], amount),
        mix(start[2], end[2], amount),
    )


def font(size: int, *, bold: bool = False) -> pg.font.Font:
    return pg.font.SysFont("verdana", size, bold=bold)
