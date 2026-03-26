#Author: Marcel
import pygame as pg
import pygame_widgets as pw
from pygame_widgets.button import ButtonArray
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from pygame_widgets.toggle import Toggle
from client.screens.base_screen import BaseScreen
from state import ClientSettings
from typing import Optional
from client import config
import json

class GraphicsScreen(BaseScreen):
    def handle_event(self, event: pg.event.Event) -> Optional[BaseScreen]:
        return None
    

    def update(self, dt: float) -> None:
        events = pg.event.get()
        pw.update(events)


    def draw(self) -> None:
         pass