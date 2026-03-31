from __future__ import annotations

import pygame

from client.sound.sounds import MUSIC_TRACKS, SFX
from shared.paths import BASE_DIR


class AudioManager:
    """
    Owns the pygame mixer and exposes volume-aware playback.

    Volumes follow a two-level model:
        effective = (master / 100) * (channel / 100)
    so a master of 50 % and effects of 80 % yields 0.40 effective gain.

    The manager also holds the loaded sound effects and music paths, so they can be played by key.
    The manager supports two channels: music and sound effects, which are controlled separately.
    """

    def __init__(self) -> None:
        """
        Initialize the mixer and load all sound effects and music paths.
        We store sound effects differently from music.
        This is because pygame supports only one music track at a time, which is controlled by pygame.mixer.music,
        while sound effects are represented by Sound objects that can be played independently.
        This also means we always need to update each sound effect's volume individually, while music volume can be set globally.
        """
        
        pygame.mixer.init()
        self._sfx: dict[str, pygame.mixer.Sound] = {
            key: pygame.mixer.Sound(BASE_DIR / path)
            for key, path in SFX.items()
        }
        self._music_paths: dict[str, str] = {
            key: str(BASE_DIR / path)
            for key, path in MUSIC_TRACKS.items()
        }
        self._current_music_key: str | None = None

        # Start with default volumes (100 %)
        self._effective_music: float = 1.0
        self._effective_sfx: float = 1.0

    def apply_settings(self, master: int, music: int, effects: int) -> None:
        """Recompute effective volumes and push them to the mixer immediately."""

        # The volume of pygame is a float in [0.0, 1.0], so we convert the percentage values.
        # Each effective volume is the product of the master volume and the channel volume.
        m = master / 100
        self._effective_music = m * (music / 100)
        self._effective_sfx   = m * (effects / 100)

        # Push the new volumes to the mixer. 
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
        if self._current_music_key == key and pygame.mixer.music.get_busy():
            return
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(self._effective_music)
        pygame.mixer.music.play(loops)
        self._current_music_key = key

    def stop_music(self) -> None:
        """Stop any currently playing music."""
        pygame.mixer.music.stop()
        self._current_music_key = None
