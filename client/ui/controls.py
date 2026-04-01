# Author: Lenard Felix, Raphael Eiden

"""
This file holds the UI control classes used in the client, such as Button, TextInput, Checkbox and Slider.
Each control has a handle_event method that processes relevant pygame events and updates the control's state accordingly
"""

from __future__ import annotations

from collections.abc import Callable
from typing import ClassVar, Literal

import pygame as pg

from client.ui.theme import (
    ACCENT,
    ACCENT_DARK,
    ACCENT_SOFT,
    DISABLED,
    PANEL,
    PANEL_ALT,
    TEXT_MUTED,
    TEXT_PRIMARY,
    blend_color,
    draw_pixel_rect,
    render_text,
)

type ButtonIcon = Literal["dice", "flag_de", "flag_en", "arrow_left", "arrow_right", "arrow_up", "arrow_down", "star"]

_ui_sfx_player: Callable[[str], None] | None = None


def configure_ui_sfx(player: Callable[[str], None] | None) -> None:
    """Register a callback used by controls to play UI sound effects."""
    global _ui_sfx_player
    _ui_sfx_player = player


def _play_ui_sfx(key: str) -> None:
    if _ui_sfx_player is not None:
        _ui_sfx_player(key)


class Button:
    """
    A button with a label and an on_click callback.
    The button supports two variants: "primary" and "secondary", which differ in their coloring.
    The button can also be disabled, which changes its appearance and prevents interaction.
    """

    _ICON_RENDERERS: ClassVar[dict[ButtonIcon, str]] = {
        "dice": "_draw_icon_dice",
        "flag_de": "_draw_icon_flag_de",
        "flag_en": "_draw_icon_flag_en",
        "arrow_left": "_draw_icon_arrow_left",
        "arrow_right": "_draw_icon_arrow_right",
        "arrow_up": "_draw_icon_arrow_up",
        "arrow_down": "_draw_icon_arrow_down",
        "star": "_draw_icon_star",
    }

    def __init__(
        self,
        rect: pg.Rect,
        label: str,
        on_click: Callable[[], None],
        *,
        variant: str = "secondary",
        enabled: bool = True,
        icon: ButtonIcon | None = None,
        abs_rect: pg.Rect | None = None
    ) -> None:
        self.rect = rect
        self.label = label
        self.on_click = on_click
        self.variant = variant
        self.enabled = enabled
        self.icon = icon
        self.abs_rect = abs_rect
        self.hovered = False
        self.pressed = False

    def handle_event(self, event: pg.event.Event) -> bool:
        if not self.enabled:
            self.pressed = False
            return False
        if event.type == pg.MOUSEMOTION:
            self.hovered = self._collides_with_cursor(event.pos)
            if self.pressed and not self.hovered:
                self.pressed = False
            return False
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.pressed = self._collides_with_cursor(event.pos)
            return self.pressed
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.pressed
            self.pressed = False
            if was_pressed and self._collides_with_cursor(event.pos):
                _play_ui_sfx("button_click")
                self.on_click()
                return True
        return False

    def _collides_with_cursor(self, pos: tuple[float, float]) -> bool:
        if self.abs_rect is not None:
            return self.abs_rect.collidepoint(pos)
        else:
            return self.rect.collidepoint(pos)

    def draw(self, surface: pg.Surface, font: pg.font.Font) -> None:
        if not self.enabled:
            fill = blend_color(PANEL_ALT, DISABLED, 0.45)
            text_color = blend_color(TEXT_MUTED, DISABLED, 0.5)
        elif self.variant == "primary":
            fill = ACCENT if not self.hovered else ACCENT_SOFT
            text_color = PANEL
        else:
            fill = PANEL_ALT if not self.hovered else blend_color(PANEL_ALT, PANEL, 0.35)
            text_color = TEXT_PRIMARY

        shadow = None if self.pressed else blend_color(fill, ACCENT_DARK, 0.35)
        draw_rect = self.rect.move(0, 2) if self.pressed else self.rect
        draw_pixel_rect(surface, draw_rect, fill, border=blend_color(fill, ACCENT_DARK, 0.45), shadow=shadow)
        if self._draw_icon(surface, text_color, draw_rect):
            return
        label = render_text(font, self.label, text_color)
        surface.blit(label, label.get_rect(center=draw_rect.center))

    def _draw_icon(self, surface: pg.Surface, color: tuple[int, int, int], rect: pg.Rect) -> bool:
        if self.icon is None:
            return False
        renderer_name = self._ICON_RENDERERS.get(self.icon)
        if renderer_name is None:
            return False
        getattr(self, renderer_name)(surface, color, rect)
        return True

    def _draw_icon_dice(self, surface: pg.Surface, color: tuple[int, int, int], rect: pg.Rect) -> None:
        die_size = min(rect.width - 20, rect.height - 16)
        die_rect = pg.Rect(0, 0, die_size, die_size)
        die_rect.center = rect.center
        pip_size = max(4, die_size // 6)
        offset = max(6, die_size // 4)
        centers = (
            (die_rect.centerx - offset, die_rect.centery - offset),
            (die_rect.centerx + offset, die_rect.centery - offset),
            (die_rect.centerx, die_rect.centery),
            (die_rect.centerx - offset, die_rect.centery + offset),
            (die_rect.centerx + offset, die_rect.centery + offset),
        )
        for center in centers:
            pip = pg.Rect(0, 0, pip_size, pip_size)
            pip.center = center
            pg.draw.rect(surface, color, pip)

    def _icon_rect(self, rect: pg.Rect, *, width: int = 28, height: int = 18) -> pg.Rect:
        icon_rect = pg.Rect(0, 0, width, height)
        icon_rect.center = rect.center
        return icon_rect

    def _draw_icon_arrow(self, surface: pg.Surface, color: tuple[int, int, int], rect: pg.Rect, direction: str) -> None:
        icon = self._icon_rect(rect, width=22, height=22)
        cx, cy = icon.center
        points = {
            "left": [(cx - 6, cy), (cx + 4, cy - 7), (cx + 4, cy + 7)],
            "right": [(cx + 6, cy), (cx - 4, cy - 7), (cx - 4, cy + 7)],
            "up": [(cx, cy - 6), (cx - 7, cy + 4), (cx + 7, cy + 4)],
            "down": [(cx, cy + 6), (cx - 7, cy - 4), (cx + 7, cy - 4)],
        }
        pg.draw.polygon(surface, color, points[direction])

    def _draw_icon_arrow_left(self, surface: pg.Surface, color: tuple[int, int, int], rect: pg.Rect) -> None:
        self._draw_icon_arrow(surface, color, rect, "left")

    def _draw_icon_arrow_right(self, surface: pg.Surface, color: tuple[int, int, int], rect: pg.Rect) -> None:
        self._draw_icon_arrow(surface, color, rect, "right")

    def _draw_icon_arrow_up(self, surface: pg.Surface, color: tuple[int, int, int], rect: pg.Rect) -> None:
        self._draw_icon_arrow(surface, color, rect, "up")

    def _draw_icon_arrow_down(self, surface: pg.Surface, color: tuple[int, int, int], rect: pg.Rect) -> None:
        self._draw_icon_arrow(surface, color, rect, "down")

    def _draw_icon_star(self, surface: pg.Surface, color: tuple[int, int, int], rect: pg.Rect) -> None:
        icon = self._icon_rect(rect, width=22, height=22)
        cx, cy = icon.center
        points = [
            (cx, cy - 9),
            (cx + 3, cy - 3),
            (cx + 10, cy - 2),
            (cx + 5, cy + 3),
            (cx + 7, cy + 10),
            (cx, cy + 6),
            (cx - 7, cy + 10),
            (cx - 5, cy + 3),
            (cx - 10, cy - 2),
            (cx - 3, cy - 3),
        ]
        pg.draw.polygon(surface, color, points)

    def _draw_icon_flag_de(self, surface: pg.Surface, color: tuple[int, int, int], rect: pg.Rect) -> None:
        del color
        flag = self._icon_rect(rect)
        stripe_height = flag.height // 3
        pg.draw.rect(surface, (20, 20, 20), pg.Rect(flag.x, flag.y, flag.width, stripe_height))
        pg.draw.rect(surface, (184, 46, 54), pg.Rect(flag.x, flag.y + stripe_height, flag.width, stripe_height))
        pg.draw.rect(
            surface,
            (232, 190, 36),
            pg.Rect(flag.x, flag.y + stripe_height * 2, flag.width, flag.height - stripe_height * 2),
        )
        pg.draw.rect(surface, blend_color(PANEL_ALT, ACCENT_DARK, 0.4), flag, 2)

    def _draw_icon_flag_en(self, surface: pg.Surface, color: tuple[int, int, int], rect: pg.Rect) -> None:
        del color
        flag = self._icon_rect(rect)
        pg.draw.rect(surface, (34, 76, 156), flag)

        diagonal_white = max(4, flag.height // 4)
        diagonal_red = max(2, diagonal_white // 2)
        diagonal_inset = 2
        top_left = (flag.x + diagonal_inset, flag.y + diagonal_inset)
        top_right = (flag.right - diagonal_inset, flag.y + diagonal_inset)
        bottom_left = (flag.x + diagonal_inset, flag.bottom - diagonal_inset)
        bottom_right = (flag.right - diagonal_inset, flag.bottom - diagonal_inset)
        pg.draw.line(surface, (240, 240, 240), top_left, bottom_right, diagonal_white)
        pg.draw.line(surface, (240, 240, 240), top_right, bottom_left, diagonal_white)
        pg.draw.line(surface, (194, 40, 48), top_left, bottom_right, diagonal_red)
        pg.draw.line(surface, (194, 40, 48), top_right, bottom_left, diagonal_red)

        white_vertical = max(4, flag.width // 5)
        white_horizontal = max(4, flag.height // 5)
        pg.draw.rect(
            surface,
            (240, 240, 240),
            pg.Rect(flag.centerx - white_vertical // 2, flag.y, white_vertical, flag.height),
        )
        pg.draw.rect(
            surface,
            (240, 240, 240),
            pg.Rect(flag.x, flag.centery - white_horizontal // 2, flag.width, white_horizontal),
        )

        red_vertical = max(2, white_vertical // 2)
        red_horizontal = max(2, white_horizontal // 2)
        pg.draw.rect(
            surface,
            (194, 40, 48),
            pg.Rect(flag.centerx - red_vertical // 2, flag.y, red_vertical, flag.height),
        )
        pg.draw.rect(
            surface,
            (194, 40, 48),
            pg.Rect(flag.x, flag.centery - red_horizontal // 2, flag.width, red_horizontal),
        )

        pg.draw.rect(surface, blend_color(PANEL_ALT, ACCENT_DARK, 0.4), flag, 2)


class TextInput:
    """
    A text input field with a label and placeholder text.
    The field can be active (focused) or inactive, which changes its appearance and whether it processes keyboard input.
    The field also has a maximum length for the input text.
    When active, the field shows a blinking cursor. This cursor needs to be updated each frame by calling the update method with the frame delta time in seconds, which advances the cursor blink timer.
    """ # TODO. the update is never called yet. should be :D

    def __init__(self, rect: pg.Rect, text: str = "", *, placeholder: str = "", max_length: int = 24) -> None:
        self.rect = rect
        self.text = text
        self.placeholder = placeholder
        self.max_length = max_length
        self.active = False
        self._cursor_visible = True
        self._cursor_timer = 0
        self._cursor_interval = 530  # ms

    def handle_event(self, event: pg.event.Event) -> bool:
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
            if self.active:
                self._cursor_visible = True
                self._cursor_timer = 0
            return self.active
        if event.type == pg.KEYDOWN and self.active:
            self._cursor_visible = True
            self._cursor_timer = 0
            if event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
                return True
            if event.key == pg.K_RETURN:
                return False
            if event.unicode.isprintable() and len(self.text) < self.max_length:
                self.text += event.unicode
                return True
        return False

    def update(self, dt: float) -> None:
        """Call each frame with delta time in seconds to advance the cursor blink."""
        if not self.active:
            self._cursor_visible = False
            self._cursor_timer = 0
            return
        self._cursor_timer += int(dt * 1000)
        if self._cursor_timer >= self._cursor_interval:
            self._cursor_timer %= self._cursor_interval
            self._cursor_visible = not self._cursor_visible

    def draw(self, surface: pg.Surface, label_font: pg.font.Font, value_font: pg.font.Font, label: str) -> None:
        caption = render_text(label_font, label, TEXT_PRIMARY)
        surface.blit(caption, (self.rect.x, self.rect.y - 28))

        fill = PANEL if self.active else blend_color(PANEL, PANEL_ALT, 0.2)
        border = ACCENT if self.active else blend_color(PANEL_ALT, ACCENT_DARK, 0.25)
        draw_pixel_rect(surface, self.rect, fill, border=border, shadow=blend_color(fill, ACCENT_DARK, 0.28))

        content = self.text if self.text else self.placeholder
        color = TEXT_PRIMARY if self.text else TEXT_MUTED
        text_surf = render_text(value_font, content, color)
        text_x = self.rect.x + 14
        text_y = self.rect.y + (self.rect.height - text_surf.get_height()) // 2
        surface.blit(text_surf, (text_x, text_y))

        cursor_width = 4
        cursor_height = max(10, value_font.get_height() - 4)
        cursor_top = text_y + max(0, (text_surf.get_height() - cursor_height) // 2)

        if self.active and self._cursor_visible and self.text:
            cursor_x = text_x + value_font.size(self.text)[0] + 2
            pg.draw.rect(surface, TEXT_PRIMARY, pg.Rect(cursor_x, cursor_top, cursor_width, cursor_height))
        elif self.active and self._cursor_visible and not self.text:
            # Cursor at start position when field is empty (skip placeholder offset)
            cursor_x = text_x + 1
            pg.draw.rect(surface, TEXT_MUTED, pg.Rect(cursor_x, cursor_top, cursor_width, cursor_height))

class Checkbox:
    """
    A checkbox with a label and a boolean value.
    The checkbox can be toggled by clicking on it, which changes its value and appearance.
    The label is rendered to the right of the checkbox.
    """

    def __init__(self, rect: pg.Rect, label: str, value: bool) -> None:
        self.rect = rect
        self.label = label
        self.value = value

    def handle_event(self, event: pg.event.Event) -> bool:
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.value = not self.value
            _play_ui_sfx("button_click")
            return True
        return False

    def draw(self, surface: pg.Surface, label_font: pg.font.Font) -> None:
        box = pg.Rect(self.rect.x, self.rect.y + 2, 24, 24)
        draw_pixel_rect(surface, box, blend_color(PANEL_ALT, PANEL, 0.55), border=blend_color(PANEL_ALT, ACCENT_DARK, 0.4))
        if self.value:
            pg.draw.line(surface, ACCENT, (box.x + 5, box.y + 13), (box.x + 10, box.y + 18), 3)
            pg.draw.line(surface, ACCENT, (box.x + 10, box.y + 18), (box.x + 19, box.y + 7), 3)
        label = render_text(label_font, self.label, TEXT_PRIMARY)
        surface.blit(label, (box.right + 16, self.rect.y))


class Slider:
    """
    A horizontal slider with a label, a percentage value and a range defined by minimum and maximum.
    The slider can be dragged by clicking and holding the mouse button on it, which updates the value according to the horizontal mouse position relative to the slider's rectangle.
    The label is rendered above the slider, and the current value is rendered to the right of the slider.
    The value is represented as a percentage, and the slider's fill corresponds to the percentage of the value within the defined range.
    """
    
    def __init__(
        self,
        rect: pg.Rect,
        label: str,
        value: int,
        *,
        minimum: int = 0,
        maximum: int = 100,
        step: int = 1,
        value_formatter: Callable[[int], str] | None = None,
        show_steps: bool = False,
    ) -> None:
        self.rect = rect
        self.label = label
        self.value = value
        self.minimum = minimum
        self.maximum = maximum
        self.step = max(1, step)
        self.value_formatter = value_formatter
        self.show_steps = show_steps
        self.dragging = False

    def _set_from_mouse(self, x: int) -> bool:
        previous_value = self.value
        amount = (x - self.rect.x) / max(1, self.rect.width)
        amount = max(0.0, min(1.0, amount))
        raw_value = self.minimum + amount * (self.maximum - self.minimum)
        stepped_value = int(round(raw_value / self.step) * self.step)
        self.value = max(self.minimum, min(self.maximum, stepped_value))
        return self.value != previous_value

    def handle_event(self, event: pg.event.Event) -> bool:
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.rect.inflate(0, 24).collidepoint(event.pos):
            self.dragging = True
            changed = self._set_from_mouse(event.pos[0])
            if changed:
                _play_ui_sfx("button_click")
            return True
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            return False
        if event.type == pg.MOUSEMOTION and self.dragging:
            changed = self._set_from_mouse(event.pos[0])
            if changed:
                _play_ui_sfx("button_click")
                return True
            return False
        return False

    def draw(self, surface: pg.Surface, label_font: pg.font.Font, value_font: pg.font.Font) -> None:
        label = render_text(label_font, self.label, TEXT_PRIMARY)
        surface.blit(label, (self.rect.x, self.rect.y - 32))
        value_text = f"{self.value}%" if self.value_formatter is None else self.value_formatter(self.value)
        value = render_text(value_font, value_text, TEXT_MUTED)
        surface.blit(value, value.get_rect(midright=(self.rect.right, self.rect.y - 16)))

        track = self.rect.inflate(0, 10)
        draw_pixel_rect(surface, track, blend_color(PANEL_ALT, PANEL, 0.1), border=blend_color(PANEL_ALT, ACCENT_DARK, 0.25))

        if self.show_steps and self.maximum > self.minimum:
            step_count = (self.maximum - self.minimum) // self.step
            dot_size = 4
            dot_y = track.centery - dot_size // 2
            dot_color = blend_color(PANEL_ALT, ACCENT_DARK, 0.45)
            for index in range(1, step_count):
                ratio = index / max(1, step_count)
                dot_x = int(round(self.rect.x + ratio * self.rect.width)) - dot_size // 2
                pg.draw.rect(surface, dot_color, pg.Rect(dot_x, dot_y, dot_size, dot_size))

        fill_width = int(self.rect.width * ((self.value - self.minimum) / max(1, self.maximum - self.minimum)))
        if fill_width > 0:
            fill_rect = pg.Rect(self.rect.x, self.rect.y - 1, fill_width, self.rect.height + 2)
            draw_pixel_rect(surface, fill_rect, ACCENT, border=blend_color(ACCENT, ACCENT_DARK, 0.35))
        knob_x = max(self.rect.x, min(self.rect.right - 18, self.rect.x + fill_width - 9))
        knob = pg.Rect(knob_x, self.rect.y - 8, 18, self.rect.height + 16)
        draw_pixel_rect(surface, knob, PANEL, border=blend_color(PANEL, ACCENT_DARK, 0.45), shadow=blend_color(PANEL, ACCENT_DARK, 0.25))
