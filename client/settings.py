from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ClientSettings:
    master_volume: int = 82
    music_volume: int = 68
    effects_volume: int = 86

    fullscreen: bool = False

    def reset_audio(self) -> None:
        self.master_volume = 82
        self.music_volume = 68
        self.effects_volume = 86

    def reset_graphics(self) -> None:
        self.fullscreen = False
