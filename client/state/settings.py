from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ClientSettings:
    master_volume: int = 82
    music_volume: int = 68
    effects_volume: int = 86

    fullscreen: bool = False

    # TODO: Get and Set functions that also save to disk, and load from disk
