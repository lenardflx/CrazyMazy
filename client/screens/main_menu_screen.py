from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from client.config import WINDOW_TITLE
from client.screens.menu_screen import MenuScreen
from client.screens.scene_types import SceneTypes

if TYPE_CHECKING:
    from client.screens.scene_manager import SceneManager


class MainMenuScreen(MenuScreen):
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

    def _quit(self) -> None:
        pg.event.post(pg.event.Event(pg.QUIT))
