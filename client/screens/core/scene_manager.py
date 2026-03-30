# Author: Lenard Felix

from __future__ import annotations

import pygame

from sys import platform
from client.config import WINDOW_WIDTH, WINDOW_HEIGHT
from client.lang import language_service
from client.sound.manager import AudioManager
from client.network.client_connection import ClientConnection
from client.network.services.game_service import GameService
from client.network.services.lobby_service import LobbyService
from client.network.state import ClientState
from client.screens.core.base_screen import BaseScreen
from client.screens.core.scene_types import SceneTypes
from client.screens.core.screen_factory import create_screen
from client.screens.core.transport_sync import TransportSync
from client.state.runtime_state import RuntimeState
from client.state.app_data import ClientData
from shared.game.snapshot import SnapshotGameState


class SceneManager:
    """
    The SceneManager is responsible for managing the current screen and handling scene transitions.
    """

    def __init__(
        self,
        connection: ClientConnection,
        transport_state: ClientState,
        surface: pygame.Surface,
        audio: AudioManager,
    ) -> None:
        # The SceneManager holds references to the connection, surface and audio manager, which it passes to the screens it creates.
        self.connection = connection
        self.surface = surface
        self.audio = audio
        self.client_settings = ClientData()
        self.runtime_state = RuntimeState()
        self.lobby_service = LobbyService(connection, self.runtime_state)
        self.game_service = GameService(connection)

        # The current scene and screen. NOTE: Can probably be simplified to a single attribute
        self.current_scene: SceneTypes | None = None
        self.current_screen: BaseScreen | None = None

        # The transport sync is responsible for syncing the transport state with the runtime state and determining if a scene change is necessary.
        self._transport_sync = TransportSync(transport_state, self.runtime_state)

        # Apply the initial audio settings
        self.audio.apply_settings(
            self.client_settings.master_volume,
            self.client_settings.music_volume,
            self.client_settings.effects_volume,
        )

    def go_to(self, scene: SceneTypes) -> None:
        """Switch to a new scene and create the corresponding screen."""
        if scene == self.current_scene:
            return
        self.current_scene = scene
        self.current_screen = create_screen(scene, self.surface, self)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Pass a pygame event to the current screen for handling."""
        if self.current_screen is not None:
            self.current_screen.handle_event(event)

    def tick(self, dt: float) -> None:
        """Update the current screen and draw it to the surface."""
        if self.current_screen is not None:
            self.current_screen.update(dt)
            self.current_screen.draw()
        pygame.display.flip()

    def apply_fullscreen(self, fullscreen: bool) -> None:
        if fullscreen:
            # TODO: Fix this workaround so Windows also gets scaled
            if platform == "win32":
                win_width, win_height = pygame.display.get_desktop_sizes()[0]
                pygame.display.set_mode((win_width, win_height), pygame.NOFRAME)
            else:
                pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        else:
            pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    def sync_transport(self) -> None:
        target, error = self._transport_sync.sync()
        if error is not None:
            self.current_screen.error_message = language_service.get_message(error)
        if target is not None:
            self.go_to(target)

    @property
    def game_state(self) -> SnapshotGameState | None:
        """
        Since the transport sync is supposed to be private, we expose the game state through a property here for screens that need it.
        """
        
        return self._transport_sync.game_state
