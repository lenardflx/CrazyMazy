from __future__ import annotations

import json
import os
from client.state.languages import languages as langs
from client.state.stats_data import Stats

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
        self.accessibility_highlight_tiles: bool = False
        self.name: str = ""
        self.language: langs = langs.ENGLISH

        self.tutorial: bool = False
        self.stats = Stats()

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

    def set_accessibility_highlight_tiles(self, value: bool) -> None:
        """Set whether the viewer tile and target tile should be highlighted on the board."""
        self.accessibility_highlight_tiles = value


    def set_language(self, val_language: langs) -> None:
        """Set the language preference."""
        self.language = val_language if isinstance(val_language, langs) else langs(val_language)


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

    def get_accessibility_highlight_tiles(self) -> bool:
        return self.accessibility_highlight_tiles

    def get_language(self) -> langs:
        return self.language

    def get_tutorial(self) -> bool:
        return self.tutorial

    def get_stats(self) -> Stats:
        """Return the persisted local multiplayer stats section."""
        return self.stats

    def write_JSON(self) -> None:
        """Persist the current settings and nested stats to ``data/app_data.json``."""
        setting_values = {
            "master_volume": self.get_master_volume(),
            "music_volume": self.get_music_volume(),
            "effects_volume": self.get_effects_volume(),
            "fullscreen": self.get_fullscreen(),
            "name": self.get_name(),
            "accessibility_highlight_tiles": self.get_accessibility_highlight_tiles(),
            "language": self.get_language().value,
            "tutorial": self.get_tutorial(),
            "stats": self.stats.to_dict(),
        }
        with open(BASE_DIR / "data/app_data.json", mode="w", encoding="utf-8") as f:
            json.dump(setting_values, f, indent=4)

    def read_JSON(self) -> None:
        """Load settings and stats from ``data/app_data.json``.

        Silently does nothing if the file is missing or malformed. The
        ``stats`` section is delegated to :class:`client.state.stats_data.Stats`
        for parsing so old files keep loading safely.
        """
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
                case "accessibility_highlight_tiles":
                    self.set_accessibility_highlight_tiles(val)
                case "language":
                    self.set_language(val)
                case "tutorial":
                    self.set_tutorial(val)
                case "stats":
                    self.stats = Stats.from_dict(val)
                case other:
                    raise NotImplementedError("attribute not implemented in json: " + other)
