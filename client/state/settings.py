from __future__ import annotations

from dataclasses import dataclass
from pygame.locals import HWSURFACE, DOUBLEBUF, NOFRAME, RESIZABLE
import json
from shared.state.textures import BASE_DIR

FULLSCREEN_FLAGS = HWSURFACE | DOUBLEBUF | NOFRAME
RESIZABLE_FLAGS = HWSURFACE | DOUBLEBUF | RESIZABLE

#FIXME: man kann die Attribute zu Klassenattributen machen, um die von außen zu ändern
class ClientSettings:
    master_volume: int = 100
    music_volume: int = 100
    effects_volume: int = 100

    fullscreen: bool = False

        # initialize last known user's setting
        #read_JSON()
        
    #fullscreen wird umgangen mittels pygame.display.get_desktop_sizes()[0] -> als neue WindowDimensionen
    #und die flags sind dann HWSURFACE | DOUBLEBUF | NOFRAME bzw 1073741857
    @classmethod
    def set_master_volume(cls, val_volume:int)->None:
        if val_volume > 100 or val_volume < 0:
            raise ValueError("value has to be between 0 and 100")
        cls.master_volume = val_volume

    @classmethod
    def set_music_volume(cls, val_volume:int)->None:
        if val_volume > 100 or val_volume < 0:
            raise ValueError("value has to be between 0 and 100")
        cls.music_volume = val_volume

    @classmethod
    def set_effects_volume(cls, val_volume:int)->None:
        if val_volume > 100 or val_volume < 0:
            raise ValueError("value has to be between 0 and 100")
        cls.effects_volume = val_volume

    @classmethod
    def toggle_fullscreen(cls):
        cls.fullscreen = not cls.fullscreen
    
    @classmethod
    def get_master_volume(cls)->int:
        return cls.master_volume
    
    @classmethod
    def get_music_volume(cls)->int:
        return cls.music_volume

    @classmethod
    def get_effects_volume(cls)->int:
        return cls.effects_volume

    @classmethod
    def get_flags(cls)->int:
        if cls.fullscreen:
            return 1073741857
        else:
            return 1073741841
  
    @classmethod
    def write_JSON(cls)->None:
        setting_values = {
            "master_volume": cls.get_master_volume(),
            "music_volume": cls.get_music_volume(),
            "effects_volume": cls.get_effects_volume(),
            "flags": cls.get_flags()
        }
        with open(BASE_DIR / "client/state/settings_data.json", mode="w", encoding="utf-8") as f:
            json.dump(setting_values, f)

    @classmethod
    def read_JSON(cls)->None:
        with open(BASE_DIR / "client/state/settings_data.json", mode="r", encoding="utf-8") as f:
            read_settings_data = json.load(f)
        for name, val in read_settings_data.items():
            match name:
                case "master_volume":
                    cls.set_master_volume(val)
                case "music_volume":
                    cls.set_music_volume(val)
                case "effects_volume":
                    cls.set_effects_volume(val)
                case "fullscreen":
                    cls.toggle_fullscreen()
                case _:
                    raise NotImplementedError("attribute not implemented in json")