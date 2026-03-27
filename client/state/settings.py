from __future__ import annotations

import json
import pygame
from client.config import WINDOW_WIDTH, WINDOW_HEIGHT

from shared.paths import BASE_DIR
from sys import platform

#FIXME: man kann die Attribute zu Klassenattributen machen, um die von außen zu ändern
class ClientSettings:
    def __init__(self):
        self.master_volume: int = 100
        self.music_volume: int = 100
        self.effects_volume: int = 100

        self.fullscreen: bool = False

        # initialize last known user's setting
        self.read_JSON()

    #fullscreen wird umgangen mittels pygame.display.get_desktop_sizes()[0] -> als neue WindowDimensionen
    #und die flags sind dann HWSURFACE | DOUBLEBUF | NOFRAME bzw 1073741857

    def set_master_volume(self, val_volume:int)->None:
        if val_volume > 100 or val_volume < 0:
            raise ValueError("value has to be between 0 and 100")
        self.master_volume = val_volume
        self.write_JSON()


    def set_music_volume(self, val_volume:int)->None:
        if val_volume > 100 or val_volume < 0:
            raise ValueError("value has to be between 0 and 100")
        self.music_volume = val_volume
        self.write_JSON()


    def set_effects_volume(self, val_volume:int)->None:
        if val_volume > 100 or val_volume < 0:
            raise ValueError("value has to be between 0 and 100")
        self.effects_volume = val_volume
        self.write_JSON()

    def set_fullscreen(self, val_fullscreen:bool)->None:
        self.fullscreen = val_fullscreen
        if self.fullscreen:
            if platform == "win32":
                pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        else:
            pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.write_JSON()


    def get_master_volume(self)->int:
        return self.master_volume
    

    def get_music_volume(self)->int:
        return self.music_volume


    def get_effects_volume(self)->int:
        return self.effects_volume


    def get_fullscreen(self)->bool:
        return self.fullscreen

    def write_JSON(self)->None:
        setting_values = {
            "master_volume": self.get_master_volume(),
            "music_volume": self.get_music_volume(),
            "effects_volume": self.get_effects_volume(),
            "fullscreen": self.get_fullscreen(),
        }
        with open(BASE_DIR / "data/settings_data.json", mode="w", encoding="utf-8") as f:
            json.dump(setting_values, f)


    def read_JSON(self)->None:
        try:
            with open(BASE_DIR / "data/settings_data.json", mode="r", encoding="utf-8") as f:
                read_settings_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return
        for name, val in read_settings_data.items():
            match name:
                case "master_volume":
                    self.set_master_volume(val)
                case "music_volume":
                    self.set_music_volume(val)
                case "effects_volume":
                    self.set_effects_volume(val)
                case "fullscreen":
                    self.set_fullscreen(val)
                case _:
                    raise NotImplementedError("attribute not implemented in json")
