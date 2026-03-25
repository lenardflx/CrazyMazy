# Author: Lenard Felix, Christopher Ionescu

from __future__ import annotations
import pygame as pg
import pygame_widgets as pw
from pygame_widgets.button import Button
from typing import Optional
from client.screens.base_screen import BaseScreen

class MainMenuScreen(BaseScreen):
    def __init__(self, surface: pg.Surface) -> None:
        self.surface = surface
        
        #Erzeuge den Quit Button
        self.quit_button = Button(
        self.surface, 300, 300, 400, 200, text='Quit',
        fontSize=50, margin=20,
        image = pg.image.load("assets\\images\\Buttons and UI\\PlaceholderMenuButton.png"),
        pressedColour=(0, 200, 200), radius=20,
        onClick=lambda: pg.event.post(pg.event.Event(pg.QUIT))
        )

    def handle_event(self, event: pg.event.Event) -> Optional[BaseScreen]:
        print(event)

    def update(self, dt: float) -> None:
        events = pg.event.get()
        pw.update(events)

    def draw(self) -> None:
        pass


