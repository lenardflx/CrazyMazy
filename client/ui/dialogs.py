# Author: Lenard Felix

"""
This file holds dialog classes for the client, which are used to display modal dialogs for confirming actions or making choices.
Each dialog is rendered with a semi-transparent overlay, to visually separate it from the underlying content.
"""

from __future__ import annotations

from collections.abc import Callable

import pygame as pg

from client.ui.controls import Button
from client.ui.theme import PANEL, PANEL_SHADOW, TEXT_MUTED, TEXT_PRIMARY, font

ChoiceSpec = tuple[str, Callable[[], None], str]


class BaseDialog:
    """Shared base class for modal dialogs."""

    WIDTH = 440
    OVERLAY_COLOR = (10, 12, 18, 120)
    SHADOW_OFFSET_Y = 6
    BORDER_RADIUS = 20
    TITLE_X = 24
    TITLE_Y = 22
    BODY_X = 24
    BODY_Y = 62

    def __init__(
        self,
        surface_rect: pg.Rect,
        title: str,
        message: str,
        rect: pg.Rect,
    ) -> None:
        self.surface_rect = surface_rect
        self.title = title
        self.message = message
        self.rect = rect

        self.title_font = font(28, bold=True)
        self.body_font = font(18)
        self.button_font = font(18, bold=True)

    def handle_buttons(self, event: pg.event.Event, buttons: list[Button]) -> bool:
        handled = False
        for button in buttons:
            handled = button.handle_event(event) or handled
        return handled

    def draw_frame(self, surface: pg.Surface) -> None:
        overlay = pg.Surface(self.surface_rect.size, pg.SRCALPHA)
        overlay.fill(self.OVERLAY_COLOR)
        surface.blit(overlay, (0, 0))

        shadow = self.rect.move(0, self.SHADOW_OFFSET_Y)
        pg.draw.rect(surface, PANEL_SHADOW, shadow, border_radius=self.BORDER_RADIUS)
        pg.draw.rect(surface, PANEL, self.rect, border_radius=self.BORDER_RADIUS)

    def draw_text(self, surface: pg.Surface, *, body_y: int | None = None) -> None:
        title = self.title_font.render(self.title, True, TEXT_PRIMARY)
        body = self.body_font.render(self.message, True, TEXT_MUTED)

        surface.blit(title, (self.rect.x + self.TITLE_X, self.rect.y + self.TITLE_Y))
        surface.blit(body, (self.rect.x + self.BODY_X, self.rect.y + (body_y if body_y is not None else self.BODY_Y)))

    def draw_buttons(self, surface: pg.Surface, buttons: list[Button]) -> None:
        for button in buttons:
            button.draw(surface, self.button_font)


class ConfirmDialog(BaseDialog):
    """
    The ConfirmDialog is a modal dialog that displays a title, a message and two buttons for confirming or canceling an action.
    The dialog can be closed by clicking either the confirm or cancel button, which triggers the corresponding callback functions.
    """

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
        rect = pg.Rect(surface_rect.centerx - 220, surface_rect.centery - 110, self.WIDTH, 220)
        super().__init__(surface_rect, title, message, rect)

        self.cancel_button = Button(
            pg.Rect(self.rect.x + 34, self.rect.bottom - 68, 160, 42),
            cancel_label,
            on_cancel,
        )
        self.confirm_button = Button(
            pg.Rect(self.rect.right - 194, self.rect.bottom - 68, 160, 42),
            confirm_label,
            on_confirm,
            variant="primary",
        )

    def handle_event(self, event: pg.event.Event) -> bool:
        return self.handle_buttons(event, [self.cancel_button, self.confirm_button])

    def draw(self, surface: pg.Surface) -> None:
        self.draw_frame(surface)
        self.draw_text(surface, body_y=72)
        self.draw_buttons(surface, [self.cancel_button, self.confirm_button])


class ChoiceDialog(BaseDialog):
    """
    The ChoiceDialog is a modal dialog that displays a title, a message and a list of buttons for making choices and a cancel button.
    Each choice button is rendered vertically below the message, and the cancel button is rendered at the bottom of the dialog.
    Clicking a choice button triggers its corresponding callback function, while clicking the cancel button triggers the on_cancel callback.
    """

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
        height = 190 + len(choices) * 54
        rect = pg.Rect(surface_rect.centerx - 220, surface_rect.centery - height // 2, self.WIDTH, height)
        super().__init__(surface_rect, title, message, rect)

        self.choice_buttons: list[Button] = []
        for index, (label, on_click, variant) in enumerate(choices):
            button_rect = pg.Rect(
                self.rect.x + 34,
                self.rect.y + 96 + index * 54,
                self.rect.width - 68,
                42,
            )
            self.choice_buttons.append(Button(button_rect, label, on_click, variant=variant))

        self.cancel_button = Button(
            pg.Rect(self.rect.x + 34, self.rect.bottom - 58, self.rect.width - 68, 42),
            cancel_label,
            on_cancel,
        )

    def handle_event(self, event: pg.event.Event) -> bool:
        return self.handle_buttons(event, [*self.choice_buttons, self.cancel_button])

    def draw(self, surface: pg.Surface) -> None:
        self.draw_frame(surface)
        self.draw_text(surface)
        self.draw_buttons(surface, self.choice_buttons)
        self.cancel_button.draw(surface, self.button_font)
