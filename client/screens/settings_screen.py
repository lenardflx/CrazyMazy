#Author: Marcel

from __future__ import annotations

import pygame as pg
import pygame_widgets as pw
import client.screens.scene_manager as scene_manager

from pygame_widgets.button import ButtonArray
from client.screens.base_screen import BaseScreen
from typing import Optional
from client import config
from shared.state.textures import UI_IMAGES

gray = (200, 200, 200)

class SettingsScreen(BaseScreen):
    #Button width und Button height
    bw = 120
    bh = 40

    def __init__(self, surface: pg.Surface, sm: scene_manager.SceneManager) -> None:
        self.SceneManager = sm
        self.SceneTypes = scene_manager.SceneTypes
        self.surface = surface
        self.surface.fill(gray)#!richtigen Hintergrund hinzufügen
        
        #Erzeuge die Buttons
        self.create_settings_buttons()


    def handle_event(self, event: pg.event.Event) -> Optional[BaseScreen]:
        return None
    
    def update(self, dt: float) -> None:
        events = pg.event.get()
        pw.update(events)
    
    def draw(self) -> None:
        pass

    def create_settings_buttons(self):
        self.settings_buttons = ButtonArray(
        self.surface,
        0,                         #x
        config.WINDOW_HEIGHT*0.1,  #y
        config.WINDOW_WIDTH,
        config.WINDOW_HEIGHT,
        (1, 3), #ButtonMatrix
        border=100,
        image = pg.transform.scale(UI_IMAGES["BUTTONS"], (self.bw, self.bh)),
        texts=('Back to Menu', 'Graphics', 'Sound'),
        onClicks=(lambda: self.SceneManager.set_next_scene(self.SceneTypes.MAIN_MENU), 
                  lambda: print('Graphics'), lambda: print('Sound')),#! hier Screen Connections einfügen
        colour=(180, 180, 180)
        )


