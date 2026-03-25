# Author: Lenard Felix, Christopher Ionescu

from __future__ import annotations

import pygame as pg
import pygame_widgets as pw
import client.screens.scene_manager as scene_manager

from pygame_widgets.button import Button, ButtonArray
from typing import Optional
from client.screens.base_screen import BaseScreen
from shared.state.textures import UI_IMAGES

class MainMenuScreen(BaseScreen):
    #Button width und Button height
    bw = 120
    bh = 40

    def __init__(self, surface: pg.Surface, sm: scene_manager.SceneManager) -> None:
        self.SceneManager = sm
        self.SceneTypes = scene_manager.SceneTypes
        self.surface = surface
        
        #Erzeuge die Buttons
        self.create_quit_button()
        self.create_settings_button()


    def handle_event(self, event: pg.event.Event) -> Optional[BaseScreen]:
        pass

    def update(self, dt: float) -> None:
        events = pg.event.get()
        pw.update(events)

    def draw(self) -> None:
        pass

    def create_quit_button(self):
        self.quit_button = Button(
        self.surface, 300, 300, self.bw, self.bh, text='Quit', fontSize=20, margin=0,
        image = pg.transform.scale(UI_IMAGES["BUTTONS"], (self.bw, self.bh)),
        onClick=lambda: pg.event.post(pg.event.Event(pg.QUIT))
        )

    def create_settings_button(self):
        self.settings_button = Button(
        self.surface, 600, 300, self.bw, self.bh, text='Settings', fontSize=20, margin=0,
        image = pg.transform.scale(UI_IMAGES["BUTTONS"], (self.bw, self.bh)),
        onClick=lambda: self.SceneManager.set_next_scene(self.SceneTypes.SETTINGS)
        )

