from __future__ import annotations

import pygame

from client.sound.sounds import MUSIC_TRACKS, SFX
from shared.paths import BASE_DIR


class AudioManager:
    """Owns the pygame mixer and exposes volume-aware playback.

    Volumes follow a two-level model:
        effective = (master / 100) * (channel / 100)
    so a master of 50 % and effects of 80 % yields 0.40 effective gain.
    """

    def __init__(self) -> None:
        pygame.mixer.init()
        self._sfx: dict[str, pygame.mixer.Sound] = {
            key: pygame.mixer.Sound(BASE_DIR / path)
            for key, path in SFX.items()
        }
        self._music_paths: dict[str, str] = {
            key: str(BASE_DIR / path)
            for key, path in MUSIC_TRACKS.items()
        }
        self._effective_music: float = 1.0
        self._effective_sfx: float = 1.0

    def apply_settings(self, master: int, music: int, effects: int) -> None:
        """Recompute effective volumes and push them to the mixer immediately."""
        m = master / 100
        self._effective_music = m * (music / 100)
        self._effective_sfx   = m * (effects / 100)

        pygame.mixer.music.set_volume(self._effective_music)
        for sound in self._sfx.values():
            sound.set_volume(self._effective_sfx)

    def play_sfx(self, key: str) -> None:
        """Play a sound effect by key, if it exists."""
        sound = self._sfx.get(key)
        if sound is not None:
            sound.play()

    def play_music(self, key: str, *, loops: int = -1) -> None:
        """Play a music track by key, if it exists."""
        path = self._music_paths.get(key)
        if path is None:
            return
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(self._effective_music)
        pygame.mixer.music.play(loops)

    def stop_music(self) -> None:
        """Stop any currently playing music."""
        pygame.mixer.music.stop()
