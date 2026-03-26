#Author: Marcel
import pygame as pg
import pygame_widgets as pw
from pygame_widgets.button import ButtonArray
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from pygame_widgets.toggle import Toggle
from client.screens.base_screen import BaseScreen
from typing import Optional
from client import config
import json

class GraphicsScreen(BaseScreen):
    def handle_event(self, event: pg.event.Event) -> Optional[BaseScreen]:
        return None
    
    def update(self, dt: float) -> None:
        events = pg.event.get()
        pw.update(events)
     
    #TODO: send commented numbers to GameSettings
    def change_flags(self, flag:int):
        match flag:
            case 0:#resizeable
                pass #1073741841
            case 1:#mockup fullscreen
                pass #1073741857
            case 2:#standard / no flags
                pass # 0

    def draw(self) -> None:
         pass