# Author: Lenard Felix
 
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from client.config import SERVER_HOST, SERVER_PORT, WINDOW_TITLE
from client.lang import DisplayMessage, language_service
from client.ui.controls import Button
from client.screens.menu.menu_screen import MenuScreen
from client.screens.core.scene_types import SceneTypes
from client.ui.theme import TEXT_MUTED, render_text

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager

#Hauptmenü
class MainMenuScreen(MenuScreen):
    """The main menu screen. Entry point after connecting to the server. Provides navigation to all top-level scenes."""

    def __init__(self, surface: pg.Surface, scene_manager: SceneManager) -> None:
        super().__init__(
            surface,
            scene_manager,
            title=WINDOW_TITLE,
            is_main_menu=True,
            buttons=[
                (language_service.get_message(DisplayMessage.MAIN_MENU_CREATE), SceneTypes.CREATE_LOBBY, "primary"),
                (language_service.get_message(DisplayMessage.MAIN_MENU_JOIN), SceneTypes.JOIN_LOBBY, "secondary"),
                (language_service.get_message(DisplayMessage.MAIN_MENU_TUTORIAL), SceneTypes.TUTORIAL, "secondary"),
                (language_service.get_message(DisplayMessage.MAIN_MENU_OPTIONS), SceneTypes.SETTINGS, "secondary"),
                (language_service.get_message(DisplayMessage.MAIN_MENU_QUIT), self._quit, "secondary"),
            ],
        )
        self.stats_button = Button(
            pg.Rect(36, surface.get_height() - 84, 56, 56),
            "",
            lambda: self.scene_manager.go_to(SceneTypes.STATS),
            variant="secondary",
            icon="star",
        )
        
        if self.scene_manager.prompt_tutorial_on_main_menu:
            self.scene_manager.prompt_tutorial_on_main_menu = False
            self.show_choice(
                language_service.get_message(DisplayMessage.MAIN_MENU_WELCOME),
                language_service.get_message(DisplayMessage.MAIN_MENU_START_WITH_TUTORIAL),
                [
                    (language_service.get_message(DisplayMessage.MAIN_MENU_START), self._start_tutorial, "primary"),
                    (language_service.get_message(DisplayMessage.MAIN_MENU_SKIP), self._skip_tutorial, "secondary"),
                ],
                cancel_label=None,
            )

    def _start_tutorial(self) -> None:
        self.scene_manager.go_to(SceneTypes.TUTORIAL)

    def _skip_tutorial(self) -> None:
        self.scene_manager.client_settings.set_tutorial(True)

    def _quit(self) -> None:
        """Open a confirmation dialog before quitting the application."""
        self.show_confirm(
            language_service.get_message(DisplayMessage.MAIN_MENU_QUIT_TITLE),
            language_service.get_message(DisplayMessage.MAIN_MENU_QUIT_MESSAGE),
            self._post_quit,
            confirm_label=language_service.get_message(DisplayMessage.MAIN_MENU_QUIT),
        )

    def _post_quit(self) -> None:
        """Post a QUIT event into the Pygame event queue, which the main loop handles to exit cleanly."""
        pg.event.post(pg.event.Event(pg.QUIT))

    def handle_content_event(self, event: pg.event.Event) -> None:
        super().handle_content_event(event)
        self.stats_button.handle_event(event)

    def draw_content(self, rect: pg.Rect) -> None:
        super().draw_content(rect)
        self.stats_button.draw(self.surface, self.button_font)

        connection_label = render_text(
            self.xs_font,
            f"{language_service.get_message(DisplayMessage.MAIN_MENU_CONNECTED_TO)}: {SERVER_HOST}:{SERVER_PORT}",
            TEXT_MUTED,
        )
        connection_rect = connection_label.get_rect(
            bottomright=(self.surface.get_width() - 16, self.surface.get_height() - 16)
        )
        self.surface.blit(connection_label, connection_rect)
