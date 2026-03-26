from __future__ import annotations

from dataclasses import dataclass
from pygame.locals import HWSURFACE, DOUBLEBUF, NOFRAME, RESIZABLE
import json

FULLSCREEN_FLAGS = HWSURFACE | DOUBLEBUF | NOFRAME
RESIZABLE_FLAGS = HWSURFACE | DOUBLEBUF | RESIZABLE

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


    def set_music_volume(self, val_volume:int)->None:
        if val_volume > 100 or val_volume < 0:
            raise ValueError("value has to be between 0 and 100")
        self.music_volume = val_volume


    def set_effects_volume(self, val_volume:int)->None:
        if val_volume > 100 or val_volume < 0:
            raise ValueError("value has to be between 0 and 100")
        self.effects_volume = val_volume
    

    def set_flags(self, val_flag:int)->None:
        possible_flags = [1073741841, 1073741857]
        if val_flag not in possible_flags:
            raise ValueError("not a valid flag")
        self.flags = val_flag


    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
    

    def get_master_volume(self)->int:
        return self.master_volume
    

    def get_music_volume(self)->int:
        return self.music_volume


    def get_effects_volume(self)->int:
        return self.effects_volume


    def get_flags(self)->int:
        if self.fullscreen:
            return 1073741857
        else:
            return 1073741841
  
    
    def write_JSON(self)->None:
        setting_values = {
            "master_volume": self.get_master_volume(),
            "music_volume": self.get_music_volume(),
            "effects_volume": self.get_effects_volume(),
            "flags": self.get_flags()
        }
        with open("settings_data.json", mode="w", encoding="utf-8") as f:
            json.dump(setting_values, f)


    def read_JSON(self)->None:
        with open("settings_data.json", mode="r", encoding="utf-8") as f:
            read_settings_data = json.load(f)
        for name, val in read_settings_data.items():
            match name:
                case "master_volume":
                    self.set_master_volume(val)
                case "music_volumme":
                    self.set_music_volume(val)
                case "effects_volume":
                    self.set_effects_volume(val)
                case "fullscreen":
                    self.set_flags(val)
                case _:
                    raise NotImplementedError("attribute not implemented in json")