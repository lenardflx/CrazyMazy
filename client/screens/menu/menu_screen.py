# Author: Lenard Felix
 
from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import pygame as pg

from client.ui.controls import Button
from client.ui.dialogs import ChoiceDialog, ConfirmDialog
from client.ui.theme import PANEL, TEXT_MUTED, TEXT_PRIMARY
from client.screens.core.base_screen import BaseScreen
from client.screens.core.scene_types import SceneTypes

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager


BACKGROUND_COLOR = (76, 96, 122)
ButtonTarget = SceneTypes | Callable[[], None]
ButtonSpec = tuple[str, ButtonTarget, str]


class MenuScreen(BaseScreen):
    """
    Base class for all menu-style screens (main menu, lobby, settings, etc.).
    Handles the shared card layout, back button, optional inline buttons, and modal dialogs.
    Subclasses override handle_content_event and draw_content to add their own UI.
    """

    def __init__(
        self,
        surface: pg.Surface,
        scene_manager: SceneManager,
        *,
        title: str,
        is_main_menu: bool = False,
        buttons: list[ButtonSpec] | None = None,
        message: str = "",
    ) -> None:
        super().__init__(surface)
        self.scene_manager = scene_manager
        self.title = title
        self.is_main_menu = is_main_menu
        self.message = message
        self.dialog: ConfirmDialog | ChoiceDialog | None = None

        self.title_font = pg.font.SysFont("verdana", 42, bold=True)
        self.section_font = pg.font.SysFont("verdana", 24, bold=True)
        self.body_font = pg.font.SysFont("verdana", 18)
        self.small_font = pg.font.SysFont("verdana", 16)
        self.button_font = pg.font.SysFont("verdana", 20, bold=True)

        width, height = self.surface.get_size()
        self.card_rect = pg.Rect(width // 2 - 430, 120, 860, height - 180)
        self.content_rect = self.card_rect.inflate(-56, -56)
        self.back_button = None
        self.buttons: list[Button] = []
        if not self.is_main_menu:
            self.back_button = Button(
                pg.Rect(42, 34, 120, 46),
                "Back",
                lambda: self.scene_manager.go_to(SceneTypes.MAIN_MENU),
            )
        if buttons:
            self._build_buttons(buttons)

    def _build_buttons(self, specs: list[ButtonSpec]) -> None:
        """Create Button instances from the given specs and lay them out vertically."""
        button_width = 320
        button_height = 56
        gap = 74
        left = self.surface.get_width() // 2 - button_width // 2
        start_y = 240 if self.is_main_menu else self.content_rect.y + 120
        self.buttons = []
        for index, (label, target, variant) in enumerate(specs):
            rect = pg.Rect(left, start_y + index * gap, button_width, button_height)
            action = (
                (lambda scene=target: self.scene_manager.go_to(scene))
                if isinstance(target, SceneTypes)
                else target
            )
            self.buttons.append(Button(rect, label, action, variant=variant))

    def handle_event(self, event: pg.event.Event) -> None:
        """Route events to the dialog if one is open, otherwise to the back button and content."""
        if self.dialog is not None:
            # If a dialog is open, intercept all events so the screen behind it stays non-interactive.
            self.dialog.handle_event(event)
            return

        if self.back_button is not None:
            self.back_button.handle_event(event)

        self.handle_content_event(event)

    def update(self, dt: float) -> None:
        del dt

    def draw(self) -> None:
        """Draw the menu background, card panel, back button, content, and any active dialog."""
        self.surface.fill(BACKGROUND_COLOR)
        # TODO: replace the flat fill with the final menu background image.

        if self.back_button is not None:
            self.back_button.draw(self.surface, self.button_font)

        if not self.is_main_menu:
            shadow_rect = self.card_rect.move(0, 4)
            pg.draw.rect(self.surface, (64, 81, 104), shadow_rect, border_radius=28)
            pg.draw.rect(self.surface, PANEL, self.card_rect, border_radius=28)
            pg.draw.rect(self.surface, (196, 202, 210), self.card_rect, width=1, border_radius=28)
            self.draw_content(self.content_rect)
        else:
            self.draw_content(self.surface.get_rect())

        if self.dialog is not None:
            self.dialog.draw(self.surface)

    def handle_content_event(self, event: pg.event.Event) -> None:
        for button in self.buttons:
            button.handle_event(event)

    def show_confirm(self, title: str, message: str, on_confirm: Callable[[], None], *, confirm_label: str = "Confirm") -> None:
        """Open a ConfirmDialog. The dialog auto-closes on either button press before calling the callback."""
        def handle_confirm() -> None:
            self.dialog = None
            on_confirm()

        def handle_cancel() -> None:
            self.dialog = None

        self.dialog = ConfirmDialog(
            self.surface.get_rect(),
            title,
            message,
            handle_confirm,
            handle_cancel,
            confirm_label=confirm_label,
        )

    def show_choice(
        self,
        title: str,
        message: str,
        choices: list[tuple[str, Callable[[], None], str]],
        *,
        cancel_label: str = "Cancel",
    ) -> None:
        """Open a ChoiceDialog. Each choice auto-closes the dialog before firing its callback."""
        wrapped_choices: list[tuple[str, Callable[[], None], str]] = []
        for label, on_select, variant in choices:
            def handle_select(callback: Callable[[], None] = on_select) -> None:
                self.dialog = None
                callback()

            wrapped_choices.append((label, handle_select, variant))

        def handle_cancel() -> None:
            self.dialog = None

        self.dialog = ChoiceDialog(
            self.surface.get_rect(),
            title,
            message,
            wrapped_choices,
            handle_cancel,
            cancel_label=cancel_label,
        )

    def draw_content(self, rect: pg.Rect) -> None:
        """Draw the screen title, optional message, and any configured nav buttons. Subclasses call super() then add their own elements."""
        if self.is_main_menu:
            title = self.title_font.render(self.title, True, TEXT_PRIMARY)
            self.surface.blit(title, title.get_rect(center=(rect.centerx, 130)))
        else:
            title = self.title_font.render(self.title, True, TEXT_PRIMARY)
            self.surface.blit(title, (self.content_rect.x, self.content_rect.y))

        if self.message:
            text = self.body_font.render(self.message, True, TEXT_MUTED)
            if self.is_main_menu:
                self.surface.blit(text, text.get_rect(center=(rect.centerx, rect.centery + 18)))
            else:
                self.surface.blit(text, (self.content_rect.x, self.content_rect.y + 56))

        for button in self.buttons:
            button.draw(self.surface, self.button_font)
