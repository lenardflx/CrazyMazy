# Author: Lenard Felix

from __future__ import annotations

import pygame

from sys import platform
from client.config import WINDOW_WIDTH, WINDOW_HEIGHT
from client.sound.manager import AudioManager
from client.network.client_connection import ClientConnection
from client.network.state import ClientState
from client.screens.core.base_screen import BaseScreen
from client.screens.core.scene_types import SceneTypes
from client.screens.core.screen_factory import create_screen
from client.screens.core.transport_sync import TransportSync
from client.state.display_state import ClientDisplayState
from client.state.runtime_state import RuntimeState
from client.state.settings import ClientSettings


class SceneManager:
    """Coordinates the active screen, client state, and network sync."""

    def __init__(
        self,
        connection: ClientConnection,
        transport_state: ClientState,
        surface: pygame.Surface,
        audio: AudioManager,
    ) -> None:
        self.connection = connection
        self.surface = surface
        self.audio = audio
        self.client_settings = ClientSettings()
        self.display_state = ClientDisplayState()
        self.runtime_state = RuntimeState()

        self.current_scene: SceneTypes | None = None
        self.current_screen: BaseScreen | None = None

        self._transport_sync = TransportSync(transport_state, self.display_state, self.runtime_state)

        self.audio.apply_settings(
            self.client_settings.master_volume,
            self.client_settings.music_volume,
            self.client_settings.effects_volume,
        )

    #Scenenwechsel
    def go_to(self, scene: SceneTypes) -> None:
        if scene == self.current_scene:
            return
        self.current_scene = scene
        self.current_screen = create_screen(scene, self.surface, self)

    #Event Handler
    def handle_event(self, event: pygame.event.Event) -> None:
        if self.current_screen is not None:
            self.current_screen.handle_event(event)

    #Screen Update
    def tick(self, dt: float) -> None:
        if self.current_screen is not None:
            self.current_screen.update(dt)
            self.current_screen.draw()
        pygame.display.flip()

    #Vollbildmodus
    def apply_fullscreen(self, fullscreen: bool) -> None:
        if fullscreen:
            if platform == "win32":
                pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        else:
            pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    def sync_transport(self) -> None:
        target = self._transport_sync.sync()
        if target is not None:
            self.go_to(target)
