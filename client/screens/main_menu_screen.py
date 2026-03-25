# Author: Lenard Felix, Christopher Ionescu

from __future__ import annotations
import pygame as pg
import pygame_widgets as pw
from pygame_widgets.button import Button
from typing import Optional
from client.screens.base_screen import BaseScreen

class MainMenuScreen(BaseScreen):
    def handle_event(self, event: pg.event.Event) -> Optional[BaseScreen]:
        return None

    def update(self, dt: float) -> None:
        events = pg.event.get()
        pw.update(events)

    def draw(self) -> None:
        self.quit_button = Button(
        self.surface, 300, 300, 300, 200, text='Quit',
        fontSize=50, margin=20,
        image = pg.image.load("assets/images/Buttons_and_UI/PlaceholderMenuButton.png"),
        #inactiveColour=(200, 200, 0),
        pressedColour=(0, 200, 200), radius=20,
        onClick=lambda: print('Click'))


