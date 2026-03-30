from __future__ import annotations

import json

from shared.paths import BASE_DIR

# TODO: maybe make this into AppData class and add other states there like last display name, and tutorial completion status?

class ClientSettings:
    """
    Persists user preferences (volumes, fullscreen) to a JSON file and reloads them on startup.
    All setters validate their input and immediately write to disk so settings survive restarts.
    """

    def __init__(self):
        self.master_volume: int = 100
        self.music_volume: int = 100
        self.effects_volume: int = 100

        self.fullscreen: bool = False

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
        self.write_JSON()

    def set_music_volume(self, val_volume: int) -> None:
        """Set the music channel volume.

        :param val_volume: Integer percentage in [0, 100].
        :raises ValueError: If the value is out of range.
        """
        if val_volume > 100 or val_volume < 0:
            raise ValueError("value has to be between 0 and 100")
        self.music_volume = val_volume
        self.write_JSON()

    def set_effects_volume(self, val_volume: int) -> None:
        """Set the sound-effects channel volume.

        :param val_volume: Integer percentage in [0, 100].
        :raises ValueError: If the value is out of range.
        """
        if val_volume > 100 or val_volume < 0:
            raise ValueError("value has to be between 0 and 100")
        self.effects_volume = val_volume
        self.write_JSON()

    def set_fullscreen(self, val_fullscreen: bool) -> None:
        """Set the fullscreen preference."""
        self.fullscreen = val_fullscreen
        self.write_JSON()

    def get_master_volume(self) -> int:
        return self.master_volume

    def get_music_volume(self) -> int:
        return self.music_volume

    def get_effects_volume(self) -> int:
        return self.effects_volume

    def get_fullscreen(self) -> bool:
        return self.fullscreen

    def write_JSON(self) -> None:
        """Persist the current settings to data/settings_data.json."""
        setting_values = {
            "master_volume": self.get_master_volume(),
            "music_volume": self.get_music_volume(),
            "effects_volume": self.get_effects_volume(),
            "fullscreen": self.get_fullscreen(),
        }
        with open(BASE_DIR / "data/settings_data.json", mode="w", encoding="utf-8") as f:
            json.dump(setting_values, f)

    def read_JSON(self) -> None:
        """Load settings from data/settings_data.json. Silently does nothing if the file is missing or malformed."""
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
