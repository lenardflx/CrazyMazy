# Author: Lenard Felix, Christopher Ionescu

from __future__ import annotations

import pygame as pg
import pygame_widgets as pw

from pygame_widgets.button import Button
from typing import Optional
from client.screens.base_screen import BaseScreen
from shared.state.textures import TILE_IMAGES

class MainMenuScreen(BaseScreen):
    def __init__(self, surface: pg.Surface) -> None:
        self.surface = surface
        
        #Erzeuge den Quit Button
        self.quit_button = Button(
        self.surface, 300, 300, 120, 40, text='Quit',
        fontSize=20,
        margin=0,
        image = pg.transform.scale(TILE_IMAGES["BUTTONS"], (120, 40)),
        onClick=lambda: pg.event.post(pg.event.Event(pg.QUIT))
        )

    def handle_event(self, event: pg.event.Event) -> Optional[BaseScreen]:
        pass

    def update(self, dt: float) -> None:
        events = pg.event.get()
        pw.update(events)

    def draw(self) -> None:
        pass


