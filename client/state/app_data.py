from __future__ import annotations

import json
import os

from shared.paths import BASE_DIR

#Singleton
class ClientData:
    """
    Persists user preferences (volumes, fullscreen etc.) to a JSON file and reloads them on startup.
    All setters validate their input and immediately write to disk so settings survive restarts.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print('Creating the object')
            cls._instance = super(ClientData, cls).__new__(cls)
            # Put any initialization here for instancing.
        return cls._instance


    def __init__(self):
        self.master_volume: int = 100
        self.music_volume: int = 100
        self.effects_volume: int = 100
        self.fullscreen: bool = False
        self.name: str = ""
        #0 für englisch (default), 1 für deutsch
        self.language: int = 0

        self.tutorial: bool = False

        os.makedirs(os.path.dirname(BASE_DIR / "data/app_data.json"), exist_ok=True)

        # Load the last saved settings from disk, overwriting the defaults above.
        self.read_JSON()

    def set_master_volume(self, val_volume: int) -> None:
        """Set the master volume.

        :param val_volume: Integer percentage in [0, 100].
        :raises ValueError: If the value is out of range.
        """
        if val_volume > 100 or val_volume < 0:
            raise ValueError("value has to be between 0 and 100")
        self.master_volume = val_volume


    def set_music_volume(self, val_volume: int) -> None:
        """Set the music channel volume.

        :param val_volume: Integer percentage in [0, 100].
        :raises ValueError: If the value is out of range.
        """
        if val_volume > 100 or val_volume < 0:
            raise ValueError("value has to be between 0 and 100")
        self.music_volume = val_volume


    def set_effects_volume(self, val_volume: int) -> None:
        """Set the sound-effects channel volume.

        :param val_volume: Integer percentage in [0, 100].
        :raises ValueError: If the value is out of range.
        """
        if val_volume > 100 or val_volume < 0:
            raise ValueError("value has to be between 0 and 100")
        self.effects_volume = val_volume


    def set_fullscreen(self, val_fullscreen: bool) -> None:
        """Set the fullscreen preference."""
        self.fullscreen = val_fullscreen


    def set_name(self, val_name: str) -> None:
        """Set the default name for games."""
        self.name = val_name


    def set_language(self, val_language: int) -> None:
        """Set the language preference."""
        self.language = val_language


    def set_tutorial(self, val_tutorial: bool) -> None:
        """Set whether the tutorial_played has been completed."""
        self.tutorial = val_tutorial


    def get_master_volume(self) -> int:
        return self.master_volume

    def get_music_volume(self) -> int:
        return self.music_volume

    def get_effects_volume(self) -> int:
        return self.effects_volume

    def get_fullscreen(self) -> bool:
        return self.fullscreen
    
    def get_name(self) -> str:
        return self.name

    def get_language(self) -> int:
        return self.language

    def get_tutorial(self) -> bool:
        return self.tutorial

    def write_JSON(self) -> None:
        """Persist the current settings to data/app_data.json."""
        setting_values = {
            "master_volume": self.get_master_volume(),
            "music_volume": self.get_music_volume(),
            "effects_volume": self.get_effects_volume(),
            "fullscreen": self.get_fullscreen(),
            "name": self.get_name(),
            "language": self.get_language(),
            "tutorial": self.get_tutorial(),
        }
        with open(BASE_DIR / "data/app_data.json", mode="w", encoding="utf-8") as f:
            json.dump(setting_values, f)

    def read_JSON(self) -> None:
        """Load settings from data/app_data.json. Silently does nothing if the file is missing or malformed."""
        try:
            with open(BASE_DIR / "data/app_data.json", mode="r", encoding="utf-8") as f:
                read_app_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return
        for name, val in read_app_data.items():
            match name:
                case "master_volume":
                    self.set_master_volume(val)
                case "music_volume":
                    self.set_music_volume(val)
                case "effects_volume":
                    self.set_effects_volume(val)
                case "fullscreen":
                    self.set_fullscreen(val)
                case "name":
                    self.set_name(val)
                case "language":
                    self.set_language(val)
                case "tutorial":
                    self.set_tutorial(val)
                case other:
                    raise NotImplementedError("attribute not implemented in json: " + other)
