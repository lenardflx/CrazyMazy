#Author: Marcel
import pygame as pg
import pygame_widgets as pw
from pygame_widgets.button import ButtonArray
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from pygame_widgets.toggle import Toggle
from client.screens.core.base_screen import BaseScreen
from typing import Optional
from client import config

class SoundScreen(BaseScreen):
    def handle_event(self, event: pg.event.Event) -> None:
        return None
    
    def update(self, dt: float) -> None:
        events = pg.event.get()
        pw.update(events)

    def slider_for_volume(self, x, y, len, height, colour, valueColour):
        slider = Slider(self.surface, x, y, len, height, colour=colour, initial=100, max=100, valueColour=valueColour)
        output = TextBox(self.surface, int(x + len * 1.15) , y - 15, 75, 50, fontSize=30)
        output.disable()
        return slider, output
    
    def draw(self) -> None:
        #!richtigen Hintergrund hinzufügen

        x, y, slider_len, slider_height, slider_margin = int(config.WINDOW_WIDTH * 0.3), int(config.WINDOW_HEIGHT*0.35), 500, 30, int(config.WINDOW_HEIGHT * 0.15)
        gray, light_gray = (100, 100, 100), (180, 180, 180)
        master_slider, master_output = self.slider_for_volume(x, y, slider_len, slider_height, light_gray, gray)
        music_slider, music_output = self.slider_for_volume(x, y + slider_margin, slider_len, slider_height, light_gray, gray)
        effects_slider, effects_output = self.slider_for_volume(x, y + slider_margin * 2, slider_len, slider_height, light_gray, gray)
        toggle = Toggle(self.surface, x, y + slider_margin * 3, 60, 40)

        #!In den Main Loop:
        #   master_output.setText(master_slider.getValue())
        #   music_output.setText(music_slider.getValue())
        #   effects_output.setText(effects_slider.getValue())
        #
        #    pygame_widgets.update(events)
