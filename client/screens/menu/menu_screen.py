# Author: Lenard Felix
 
from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import pygame as pg

from client.config import MENU_BACKGROUND_ANIMATION_FRAMES
from client.textures import UI_IMAGES
from client.ui.controls import Button
from client.ui.dialogs import ChoiceDialog, ConfirmDialog
from client.ui.theme import PANEL, PANEL_ALT, PANEL_SHADOW, TEXT_MUTED, TEXT_PRIMARY, draw_pixel_rect, font, render_text, title_font
from client.screens.core.base_screen import BaseScreen
from client.screens.core.scene_types import SceneTypes

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager


BACKGROUND_COLOR = (76, 96, 122)
ButtonTarget = SceneTypes | Callable[[], None]
ButtonSpec = tuple[str, ButtonTarget, str]

#Oberklasse Menu Screens
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
        self.background_image: pg.Surface | None = UI_IMAGES["TITLE_BACKGROUND"]
        self.animation_state: int = 0

        self.title_font = font(34)
        self.display_title_font = title_font(72)  # ka1 — main menu title only
        self.section_font = font(24)
        self.body_font = font(18)
        self.small_font = font(16)
        self.button_font = font(20)

        width, height = self.surface.get_size()
        self.card_rect = pg.Rect(width // 2 - 430, 104, 860, height - 164)
        self.content_rect = self.card_rect.inflate(-56, -56)
        self.back_button = None
        self.buttons: list[Button] = []
        if not self.is_main_menu:
            self.back_button = Button(
                pg.Rect(42, 34, 120, 46),
                "Back",
                lambda: self.scene_manager.go_to(
                    self.scene_manager.settings_return_scene
                    if self.scene_manager.current_scene == SceneTypes.SETTINGS
                    else SceneTypes.MAIN_MENU
                ),
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
        self.update_content(dt)

    def update_content(self, dt: float) -> None:
        del dt

    def draw(self) -> None:
        """Draw the menu background, card panel, back button, content, and any active dialog."""
        self._draw_background()

        if self.back_button is not None:
            self.back_button.draw(self.surface, self.button_font)

        if not self.is_main_menu:
            draw_pixel_rect(self.surface, self.card_rect, PANEL, border=PANEL_ALT, shadow=PANEL_SHADOW)
            self.draw_content(self.content_rect)
        else:
            self.draw_content(self.surface.get_rect())

        if self.dialog is not None:
            self.dialog.draw(self.surface)

    def _draw_background(self) -> None:
        if self.background_image is None:
            self.surface.fill(BACKGROUND_COLOR)
            return
        # total time passed since the game loop started
        ms = pg.time.get_ticks()
        frame_duration = 200
        frame_index = (ms // frame_duration) % MENU_BACKGROUND_ANIMATION_FRAMES
        current_image = UI_IMAGES["TITLE_ANIMATION_" + str(frame_index)]
        scaled = pg.transform.scale(current_image, self.surface.get_size())
        self.surface.blit(scaled, (0, 0))

    def handle_content_event(self, event: pg.event.Event) -> None:
        for button in self.buttons:
            button.handle_event(event)

    def show_confirm(self, title: str, message: str, on_confirm: Callable[[], None], *, confirm_label: str = "Confirm", cancel_label: str = "Cancel") -> None:
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
            cancel_label=cancel_label,
        )

    def show_choice(
        self,
        title: str,
        message: str,
        choices: list[tuple[str, Callable[[], None], str]],
        *,
        cancel_label: str | None = "Cancel",
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
            title = render_text(self.display_title_font, self.title, TEXT_PRIMARY)
            self.surface.blit(title, title.get_rect(center=(rect.centerx, 130)))
        else:
            title = render_text(self.title_font, self.title, TEXT_PRIMARY)
            self.surface.blit(title, (self.content_rect.x, self.content_rect.y))

        if self.message:
            text = render_text(self.body_font, self.message, TEXT_MUTED)
            if self.is_main_menu:
                self.surface.blit(text, text.get_rect(center=(rect.centerx, rect.centery + 18)))
            else:
                self.surface.blit(text, (self.content_rect.x, self.content_rect.y + 56))

        for button in self.buttons:
            button.draw(self.surface, self.button_font)
