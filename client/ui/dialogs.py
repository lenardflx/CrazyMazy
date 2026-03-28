# Author: Lenard Felix
 
from __future__ import annotations

from collections.abc import Callable

import pygame as pg

from client.ui.controls import Button
from client.ui.theme import PANEL, PANEL_SHADOW, TEXT_MUTED, TEXT_PRIMARY, font

ChoiceSpec = tuple[str, Callable[[], None], str]


class ConfirmDialog:
    def __init__(
        self,
        surface_rect: pg.Rect,
        title: str,
        message: str,
        on_confirm: Callable[[], None],
        on_cancel: Callable[[], None],
        *,
        confirm_label: str = "Confirm",
        cancel_label: str = "Cancel",
    ) -> None:
        self.surface_rect = surface_rect
        self.title = title
        self.message = message
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.title_font = font(28, bold=True)
        self.body_font = font(18)
        self.button_font = font(18, bold=True)

        self.rect = pg.Rect(surface_rect.centerx - 220, surface_rect.centery - 110, 440, 220)
        self.cancel_button = Button(pg.Rect(self.rect.x + 34, self.rect.bottom - 68, 160, 42), cancel_label, self.on_cancel)
        self.confirm_button = Button(
            pg.Rect(self.rect.right - 194, self.rect.bottom - 68, 160, 42),
            confirm_label,
            self.on_confirm,
            variant="primary",
        )

    def handle_event(self, event: pg.event.Event) -> bool:
        handled = self.cancel_button.handle_event(event)
        handled = self.confirm_button.handle_event(event) or handled
        return handled

    def draw(self, surface: pg.Surface) -> None:
        overlay = pg.Surface(self.surface_rect.size, pg.SRCALPHA)
        overlay.fill((10, 12, 18, 120))
        surface.blit(overlay, (0, 0))
        shadow = self.rect.move(0, 6)
        pg.draw.rect(surface, PANEL_SHADOW, shadow, border_radius=20)
        pg.draw.rect(surface, PANEL, self.rect, border_radius=20)
        title = self.title_font.render(self.title, True, TEXT_PRIMARY)
        body = self.body_font.render(self.message, True, TEXT_MUTED)
        surface.blit(title, (self.rect.x + 24, self.rect.y + 22))
        surface.blit(body, (self.rect.x + 24, self.rect.y + 72))
        self.cancel_button.draw(surface, self.button_font)
        self.confirm_button.draw(surface, self.button_font)


class ChoiceDialog:
    def __init__(
        self,
        surface_rect: pg.Rect,
        title: str,
        message: str,
        choices: list[ChoiceSpec],
        on_cancel: Callable[[], None],
        *,
        cancel_label: str = "Cancel",
    ) -> None:
        self.surface_rect = surface_rect
        self.title = title
        self.message = message
        self.on_cancel = on_cancel
        self.title_font = font(28, bold=True)
        self.body_font = font(18)
        self.button_font = font(18, bold=True)

        height = 190 + len(choices) * 54
        self.rect = pg.Rect(surface_rect.centerx - 220, surface_rect.centery - height // 2, 440, height)
        self.choice_buttons: list[Button] = []
        for index, (label, on_click, variant) in enumerate(choices):
            button_rect = pg.Rect(self.rect.x + 34, self.rect.y + 96 + index * 54, self.rect.width - 68, 42)
            self.choice_buttons.append(Button(button_rect, label, on_click, variant=variant))
        self.cancel_button = Button(
            pg.Rect(self.rect.x + 34, self.rect.bottom - 58, self.rect.width - 68, 42),
            cancel_label,
            self.on_cancel,
        )

    def handle_event(self, event: pg.event.Event) -> bool:
        handled = False
        for button in self.choice_buttons:
            handled = button.handle_event(event) or handled
        handled = self.cancel_button.handle_event(event) or handled
        return handled

    def draw(self, surface: pg.Surface) -> None:
        overlay = pg.Surface(self.surface_rect.size, pg.SRCALPHA)
        overlay.fill((10, 12, 18, 120))
        surface.blit(overlay, (0, 0))
        shadow = self.rect.move(0, 6)
        pg.draw.rect(surface, PANEL_SHADOW, shadow, border_radius=20)
        pg.draw.rect(surface, PANEL, self.rect, border_radius=20)
        title = self.title_font.render(self.title, True, TEXT_PRIMARY)
        body = self.body_font.render(self.message, True, TEXT_MUTED)
        surface.blit(title, (self.rect.x + 24, self.rect.y + 22))
        surface.blit(body, (self.rect.x + 24, self.rect.y + 62))
        for button in self.choice_buttons:
            button.draw(surface, self.button_font)
        self.cancel_button.draw(surface, self.button_font)
