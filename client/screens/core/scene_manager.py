# Author: Lenard Felix

from __future__ import annotations

import time
from typing import TYPE_CHECKING

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
from client.ui.controls import configure_ui_sfx
from shared.game.snapshot import SnapshotGameState
from shared.lib.lobby import VALID_INSERT_TIMEOUTS, VALID_MOVE_TIMEOUTS
from shared.types.enums import GamePhase, PlayerResult

if TYPE_CHECKING:
    from client.tutorial.session import TutorialSession


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
        self.surface = surface  # display surface
        self.audio = audio
        self.client_settings = ClientData()
        self.runtime_state = RuntimeState()
        self.tutorial_session: TutorialSession | None = None
        self.prompt_tutorial_on_main_menu = not self.client_settings.get_tutorial()
        self.settings_return_scene = SceneTypes.MAIN_MENU
        self.lobby_service = LobbyService(connection, self.runtime_state)
        self.game_service = GameService(connection)

        # Internal render surface (fixed logical resolution)
        self.render_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)).convert() #!!!!

        # The current scene and screen.
        self.current_scene: SceneTypes | None = None
        self.current_screen: BaseScreen | None = None

        # Transport sync
        self._transport_sync = TransportSync(transport_state, self.runtime_state, self.client_settings)
        self._last_timer_beep_second: int | None = None

        # Apply the initial audio settings
        self.audio.apply_settings(
            self.client_settings.master_volume,
            self.client_settings.music_volume,
            self.client_settings.effects_volume,
        )
        configure_ui_sfx(self.audio.play_sfx)

    def go_to(self, scene: SceneTypes) -> None:
        """Switch to a new scene and create the corresponding screen."""
        if scene == self.current_scene:
            return
        self.current_scene = scene
        self._sync_scene_music(scene)

        # IMPORTANT: Screens now draw onto render_surface, not the display surface
        self.current_screen = create_screen(scene, self.render_surface, self) #!!!!!

    def handle_event(self, event: pygame.event.Event) -> None:
        """Pass a pygame event to the current screen for handling."""
        # if self.current_screen is not None:
        #     self.current_screen.handle_event(event)
        if self.current_screen is not None: #!!!!
            if pygame.display.is_fullscreen():
                info = pygame.display.Info()
                mx, my = pygame.mouse.get_pos()

                # Skalierungsfaktoren
                scale_x = WINDOW_WIDTH / info.current_w
                scale_y = WINDOW_HEIGHT / info.current_h

                # Umgerechnete Mausposition
                scaled_pos = (mx * scale_x, my * scale_y)

                # Event patchen
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                    event.pos = scaled_pos

            self.current_screen.handle_event(event)

    def tick(self, dt: float) -> None:
        self._play_countdown_sfx()
        if self.current_screen is not None:
            self.current_screen.update(dt)
            self.current_screen.draw()

        screen = pygame.display.get_surface()

        # --- MANUELLES FULLSCREEN-SCALING --- #!!!!
        if pygame.display.is_fullscreen():
            info = pygame.display.Info()
            scaled = pygame.transform.scale(
                self.render_surface,
                (info.current_w, info.current_h)
            )
            screen.blit(scaled, (0, 0))
        else:
            screen.blit(self.render_surface, (0, 0))

        pygame.display.flip()

    def apply_fullscreen(self, fullscreen: bool) -> None:
        if fullscreen:
            # if platform == "win32":
            #     pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # else:
            #     pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
            pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    def sync_transport(self) -> None:
        previous_state = self.game_state
        target, error = self._transport_sync.sync()
        if error is not None:
            self.current_screen.set_error_message(language_service.get_message(error))
            self.audio.play_sfx("error")
        current_state = self.game_state
        self._play_snapshot_sfx(previous_state, current_state)
        if target is not None:
            self.go_to(target)

    def go_to_settings(self, return_scene: SceneTypes) -> None:
        self.settings_return_scene = return_scene
        self.go_to(SceneTypes.SETTINGS)

    def _sync_scene_music(self, scene: SceneTypes) -> None:
        if scene in (SceneTypes.GAME, SceneTypes.TUTORIAL):
            self.audio.play_music("ingame")
            return
        self.audio.play_music("lobby")

    @property
    def game_state(self) -> SnapshotGameState | None:
        return self._transport_sync.game_state

    def _play_snapshot_sfx(
        self,
        previous_state: SnapshotGameState | None,
        current_state: SnapshotGameState | None,
    ) -> None:
        if current_state is None:
            self._last_timer_beep_second = None
            return

        if current_state.phase == GamePhase.POSTGAME and (
            previous_state is None or previous_state.phase != GamePhase.POSTGAME
        ):
            viewer = current_state.viewer_player
            if viewer is not None and viewer.result == PlayerResult.WON:
                self.audio.play_sfx("win")
            else:
                self.audio.play_sfx("lose")

        became_viewer_turn = (
            current_state.phase == GamePhase.GAME
            and current_state.viewer_turn
            and (
                previous_state is None
                or previous_state.phase != GamePhase.GAME
                or not previous_state.viewer_turn
                or previous_state.current_player_id != current_state.current_player_id
                or previous_state.turn.phase != current_state.turn.phase
            )
        )
        if became_viewer_turn:
            self.audio.play_sfx("your_turn")
            self._last_timer_beep_second = None

        if current_state.phase != GamePhase.GAME or not current_state.viewer_turn:
            self._last_timer_beep_second = None

        previous_viewer = None if previous_state is None else previous_state.viewer_player
        current_viewer = current_state.viewer_player
        if (
            previous_viewer is not None
            and current_viewer is not None
            and current_viewer.collected_treasure_count > previous_viewer.collected_treasure_count
            and current_viewer.collected_treasures
        ):
            collected = current_viewer.collected_treasures[-1]
            if collected.name == "PRINCESS":
                self.audio.play_sfx("treasure_collect_meow")
            else:
                self.audio.play_sfx("treasure_collect")

    def _play_countdown_sfx(self) -> None:
        game_state = self.game_state
        if (
            game_state is None
            or game_state.phase != GamePhase.GAME
            or not game_state.viewer_turn
            or game_state.turn.turn_end_timestamp is None
        ):
            self._last_timer_beep_second = None
            return

        remaining_ms = game_state.turn.turn_end_timestamp - (time.time_ns() // 1_000_000)
        if remaining_ms <= 0:
            self._last_timer_beep_second = None
            return

        remaining_second = (remaining_ms - 1) // 1000 + 1
        if 1 <= remaining_second <= 3 and remaining_second != self._last_timer_beep_second:
            self.audio.play_sfx("timer_beep")
            self._last_timer_beep_second = remaining_second
