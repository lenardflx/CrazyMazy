# Author: Lenard Felix
 
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from client.config import WINDOW_TITLE
from client.ui.controls import Button
from client.screens.menu.menu_screen import MenuScreen
from client.screens.core.scene_types import SceneTypes

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
                ("Create", SceneTypes.CREATE_LOBBY, "primary"),
                ("Join", SceneTypes.JOIN_LOBBY, "secondary"),
                ("Tutorial", SceneTypes.TUTORIAL, "secondary"),
                ("Options", SceneTypes.SETTINGS, "secondary"),
                ("Quit", self._quit, "secondary"),
            ],
        )
        
        if self.scene_manager.prompt_tutorial_on_main_menu:
            self.scene_manager.prompt_tutorial_on_main_menu = False
            self.show_choice(
                "Welcome",
                "Start with the tutorial?",
                [
                    ("Start", self._start_tutorial, "primary"),
                    ("Skip", self._skip_tutorial, "secondary"),
                ],
                cancel_label=None,
            )

    def _start_tutorial(self) -> None:
        self.scene_manager.go_to(SceneTypes.TUTORIAL)

    def _skip_tutorial(self) -> None:
        self.scene_manager.client_settings.set_tutorial(True)

    def _quit(self) -> None:
        """Open a confirmation dialog before quitting the application."""
        self.show_confirm("Quit Game?", "Close the client now?", self._post_quit, confirm_label="Quit")

    def _post_quit(self) -> None:
        """Post a QUIT event into the Pygame event queue, which the main loop handles to exit cleanly."""
        pg.event.post(pg.event.Event(pg.QUIT))
