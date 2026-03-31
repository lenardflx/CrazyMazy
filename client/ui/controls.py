# Author: Lenard Felix

"""
This file holds the UI control classes used in the client, such as Button, TextInput, Checkbox and Slider.
Each control has a handle_event method that processes relevant pygame events and updates the control's state accordingly
"""

from __future__ import annotations

from collections.abc import Callable

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


class Button:
    """
    A button with a label and an on_click callback.
    The button supports two variants: "primary" and "secondary", which differ in their coloring.
    The button can also be disabled, which changes its appearance and prevents interaction.
    """

    def __init__(
        self,
        rect: pg.Rect,
        label: str,
        on_click: Callable[[], None],
        *,
        variant: str = "secondary",
        enabled: bool = True,
    ) -> None:
        self.rect = rect
        self.label = label
        self.on_click = on_click
        self.variant = variant
        self.enabled = enabled
        self.hovered = False

    def handle_event(self, event: pg.event.Event) -> bool:
        if not self.enabled:
            return False
        if event.type == pg.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            return False
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.on_click()
            return True
        return False

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

        draw_pixel_rect(surface, self.rect, fill, border=blend_color(fill, ACCENT_DARK, 0.45), shadow=blend_color(fill, ACCENT_DARK, 0.35))
        label = render_text(font, self.label, text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))


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

        if self.active and self._cursor_visible and self.text:
            cursor_x = text_x + value_font.size(self.text)[0] + 2
            cursor_top = text_y + 2
            cursor_bottom = text_y + value_font.get_height() - 2
            pg.draw.rect(surface, TEXT_PRIMARY, pg.Rect(cursor_x, cursor_top, 2, max(1, cursor_bottom - cursor_top)))
        elif self.active and self._cursor_visible and not self.text:
            # Cursor at start position when field is empty (skip placeholder offset)
            cursor_x = text_x + 1
            cursor_top = text_y + 2
            cursor_bottom = text_y + value_font.get_height() - 2
            pg.draw.rect(surface, TEXT_MUTED, pg.Rect(cursor_x, cursor_top, 2, max(1, cursor_bottom - cursor_top)))

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
    
    def __init__(self, rect: pg.Rect, label: str, value: int, *, minimum: int = 0, maximum: int = 100) -> None:
        self.rect = rect
        self.label = label
        self.value = value
        self.minimum = minimum
        self.maximum = maximum
        self.dragging = False

    def _set_from_mouse(self, x: int) -> None:
        amount = (x - self.rect.x) / max(1, self.rect.width)
        amount = max(0.0, min(1.0, amount))
        self.value = int(round(self.minimum + amount * (self.maximum - self.minimum)))

    def handle_event(self, event: pg.event.Event) -> bool:
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.rect.inflate(0, 24).collidepoint(event.pos):
            self.dragging = True
            self._set_from_mouse(event.pos[0])
            return True
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            return False
        if event.type == pg.MOUSEMOTION and self.dragging:
            self._set_from_mouse(event.pos[0])
            return True
        return False

    def draw(self, surface: pg.Surface, label_font: pg.font.Font, value_font: pg.font.Font) -> None:
        label = render_text(label_font, self.label, TEXT_PRIMARY)
        surface.blit(label, (self.rect.x, self.rect.y - 32))
        value = render_text(value_font, f"{self.value}%", TEXT_MUTED)
        surface.blit(value, value.get_rect(midright=(self.rect.right, self.rect.y - 16)))

        track = self.rect.inflate(0, 10)
        draw_pixel_rect(surface, track, blend_color(PANEL_ALT, PANEL, 0.1), border=blend_color(PANEL_ALT, ACCENT_DARK, 0.25))

        fill_width = int(self.rect.width * ((self.value - self.minimum) / max(1, self.maximum - self.minimum)))
        if fill_width > 0:
            fill_rect = pg.Rect(self.rect.x, self.rect.y - 1, fill_width, self.rect.height + 2)
            draw_pixel_rect(surface, fill_rect, ACCENT, border=blend_color(ACCENT, ACCENT_DARK, 0.35))
        knob_x = max(self.rect.x, min(self.rect.right - 18, self.rect.x + fill_width - 9))
        knob = pg.Rect(knob_x, self.rect.y - 8, 18, self.rect.height + 16)
        draw_pixel_rect(surface, knob, PANEL, border=blend_color(PANEL, ACCENT_DARK, 0.45), shadow=blend_color(PANEL, ACCENT_DARK, 0.25))
