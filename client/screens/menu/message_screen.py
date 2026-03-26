# Author: Lenard Felix
 
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from client.screens.menu.menu_screen import MenuScreen

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager


class MessageScreen(MenuScreen):
    def __init__(self, surface: pg.Surface, scene_manager: SceneManager, *, title: str, message: str) -> None:
        super().__init__(
            surface,
            scene_manager,
            title=title,
            is_main_menu=False,
            message=message,
        )
