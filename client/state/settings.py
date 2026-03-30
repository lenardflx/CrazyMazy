from __future__ import annotations

import json
import pygame
from client.config import WINDOW_WIDTH, WINDOW_HEIGHT

from shared.paths import BASE_DIR
from sys import platform

#Singleton
class ClientSettings:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ClientSettings, cls).__new__(cls)
            cls._instance.read_JSON()
        return cls._instance


    def __init__(self):
        self.master_volume: int = 100
        self.music_volume: int = 100
        self.effects_volume: int = 100

        self.fullscreen: bool = False
        

    #fullscreen wird umgangen mittels pygame.display.get_desktop_sizes()[0] -> als neue WindowDimensionen
    #und die flags sind dann HWSURFACE | DOUBLEBUF | NOFRAME bzw 1073741857
    def set_master_volume(self, val_volume:int)->None:
        if val_volume > 100 or val_volume < 0:
            raise ValueError("value has to be between 0 and 100")
        self.master_volume = val_volume
        self.write_JSON()
        self.master_volume = val_volume


    #Setze die Musik-Lautstärke
    def set_music_volume(self, val_volume:int)->None:
        if val_volume > 100 or val_volume < 0:
            raise ValueError("value has to be between 0 and 100")
        self.music_volume = val_volume
        self.write_JSON()
        self.music_volume = val_volume


    #Setze die Effekt-Lautstärke
    def set_effects_volume(self, val_volume:int)->None:
        if val_volume > 100 or val_volume < 0:
            raise ValueError("value has to be between 0 and 100")
        self.effects_volume = val_volume


    #Setze den Fullscreen Status
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


    #Returnt die Master Lautstärke
    def get_master_volume(self)->int:
        return self.master_volume
    

    #Returnt die Musik Lautstärke
    def get_music_volume(self)->int:
        return self.music_volume


    #Returnt die Effekt Lautstärke
    def get_effects_volume(self)->int:
        return self.effects_volume


    #Returnt den Fullscreen Status
    def get_fullscreen(self)->bool:
        return self.fullscreen


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
            "fullscreen": self.get_fullscreen(),
            "master_volume": self.get_master_volume(),
            "music_volume": self.get_music_volume(),
            "effects_volume": self.get_effects_volume(),
            "flags": self.get_flags()
        }
        with open(BASE_DIR / "data/settings_data.json", mode="w", encoding="utf-8") as f:
            json.dump(setting_values, f)


    #Liest die lokalen Einstellungen aus der JSON
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
