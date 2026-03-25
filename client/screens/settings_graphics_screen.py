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

class GraphicsScreen(BaseScreen):
    def handle_event(self, event: pg.event.Event) -> Optional[BaseScreen]:
        return None
    
    def update(self, dt: float) -> None:
        events = pg.event.get()
        pw.update(events)
     
    def change_flags(self, flag:int):
        flags = None
        match flag:
            case 0:#resize
                with open('zahl.txt', 'w') as f:                
                    f.write(str(1073741841))
            case 1:#mockup fullscreen
                with open('zahl.txt', 'w') as f:                
                    f.write(str(1073741857))
            case 2:#standard / no flags
                with open('zahl.txt', 'w') as f:                
                    f.write(str(0))

    def draw(self) -> None:
         pass