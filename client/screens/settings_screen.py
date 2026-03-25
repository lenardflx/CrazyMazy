#Author: Marcel
import pygame as pg
import pygame_widgets as pw
from pygame_widgets.button import ButtonArray
from client.screens.base_screen import BaseScreen
from typing import Optional
from client import config

gray = (200, 200, 200)

class SettingsScreen(BaseScreen):
    def handle_event(self, event: pg.event.Event) -> Optional[BaseScreen]:
        return None
    
    def update(self, dt: float) -> None:
        events = pg.event.get()
        pw.update(events)
    
    def draw(self) -> None:
        self.surface.fill(gray)#!richtigen Hintergrund hinzufügen

        buttonArray = ButtonArray(
        self.surface,
        0,                         #x
        config.WINDOW_HEIGHT*0.1,  #y
        config.WINDOW_WIDTH,
        config.WINDOW_HEIGHT,
        (1, 3), #ButtonMatrix
        border=100,
        texts=('Back to Menu', 'Graphics', 'Sound'),
        onClicks=(lambda: print('Menu'), lambda: print('Graphics'), lambda: print('Sound')),#! hier Screen Connections einfügen
        colour=(180, 180, 180)
)

