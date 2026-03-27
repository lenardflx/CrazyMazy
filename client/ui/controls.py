# Author: Lenard Felix
 
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
)


class Button:
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

        shadow = self.rect.move(0, 2)
        pg.draw.rect(surface, blend_color(fill, ACCENT_DARK, 0.35), shadow, border_radius=18)
        pg.draw.rect(surface, fill, self.rect, border_radius=18)
        pg.draw.rect(surface, blend_color(fill, ACCENT_DARK, 0.45), self.rect, width=1, border_radius=18)
        label = font.render(self.label, True, text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))


class TextInput:
    def __init__(self, rect: pg.Rect, text: str = "", *, placeholder: str = "", max_length: int = 24) -> None:
        self.rect = rect
        self.text = text
        self.placeholder = placeholder
        self.max_length = max_length
        self.active = False

    def handle_event(self, event: pg.event.Event) -> bool:
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
            return self.active
        if event.type == pg.KEYDOWN and self.active:
            if event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
                return True
            if event.key == pg.K_RETURN:
                return False
            if event.unicode.isprintable() and len(self.text) < self.max_length:
                self.text += event.unicode
                return True
        return False

    def draw(self, surface: pg.Surface, label_font: pg.font.Font, value_font: pg.font.Font, label: str) -> None:
        caption = label_font.render(label, True, TEXT_PRIMARY)
        surface.blit(caption, (self.rect.x, self.rect.y - 28))
        fill = PANEL if self.active else blend_color(PANEL, PANEL_ALT, 0.2)
        border = ACCENT if self.active else blend_color(PANEL_ALT, ACCENT_DARK, 0.25)
        pg.draw.rect(surface, fill, self.rect, border_radius=14)
        pg.draw.rect(surface, border, self.rect, width=1, border_radius=14)
        content = self.text if self.text else self.placeholder
        color = TEXT_PRIMARY if self.text else TEXT_MUTED
        text = value_font.render(content, True, color)
        surface.blit(text, (self.rect.x + 14, self.rect.y + 10))


class Checkbox:
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
        pg.draw.rect(surface, blend_color(PANEL_ALT, PANEL, 0.55), box, border_radius=6)
        pg.draw.rect(surface, blend_color(PANEL_ALT, ACCENT_DARK, 0.4), box, width=1, border_radius=6)
        if self.value:
            pg.draw.line(surface, ACCENT, (box.x + 5, box.y + 13), (box.x + 10, box.y + 18), 3)
            pg.draw.line(surface, ACCENT, (box.x + 10, box.y + 18), (box.x + 19, box.y + 7), 3)
        label = label_font.render(self.label, True, TEXT_PRIMARY)
        surface.blit(label, (box.right + 16, self.rect.y))


class Slider:
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
        label = label_font.render(self.label, True, TEXT_PRIMARY)
        surface.blit(label, (self.rect.x, self.rect.y - 32))
        value = value_font.render(f"{self.value}%", True, TEXT_MUTED)
        surface.blit(value, value.get_rect(midright=(self.rect.right, self.rect.y - 16)))
        pg.draw.line(surface, blend_color(PANEL_ALT, TEXT_MUTED, 0.2), self.rect.midleft, self.rect.midright, 8)
        fill_width = int(self.rect.width * ((self.value - self.minimum) / max(1, self.maximum - self.minimum)))
        fill_rect = pg.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pg.draw.line(surface, ACCENT, fill_rect.midleft, fill_rect.midright, 8)
        knob_x = max(self.rect.x, min(self.rect.right, self.rect.x + fill_width))
        pg.draw.circle(surface, PANEL, (knob_x, self.rect.centery), 12)
        pg.draw.circle(surface, blend_color(PANEL, ACCENT_DARK, 0.45), (knob_x, self.rect.centery), 12, 1)
