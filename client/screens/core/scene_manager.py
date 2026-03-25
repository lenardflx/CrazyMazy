# TODO: docs

from __future__ import annotations

import pygame

from client.network.client_connection import ClientConnection
from client.network.errors import apply_server_error
from client.network.state import ClientState
from client.state.display_state import ClientDisplayState
from client.state.runtime_state import RuntimeState
from client.state.settings import ClientSettings
from client.screens.core.base_screen import BaseScreen
from client.screens.core.scene_types import SceneTypes
from client.screens.game.game_screen import GameScreen
from client.screens.game.post_game_screen import PostGameScreen
from client.screens.lobby.create_lobby_screen import CreateLobbyScreen
from client.screens.lobby.join_lobby_screen import JoinLobbyScreen
from client.screens.lobby.lobby_screen import LobbyScreen
from client.screens.menu.main_menu_screen import MainMenuScreen
from client.screens.menu.message_screen import MessageScreen
from client.screens.menu.no_server_screen import NoServerScreen
from client.screens.menu.settings_screen import SettingsScreen

#ScreenManager, mit dem die Screens gewechselt werden können
class SceneManager:
    def __init__(self, connection: ClientConnection, transport_state: ClientState) -> None:
        self.connection = connection
        self.transport_state = transport_state
        self.current_scene: SceneTypes | None = None
        self.client_settings = ClientSettings()
        self.runtime_state = RuntimeState()
        self.display_state = ClientDisplayState()
        self._seen_snapshot_version = 0
        self._seen_error_version = 0
        self._seen_game_left_version = 0

    #Wechsle zur korrekten Scene
    def switch_scene(self, scene_name: SceneTypes, surface: pygame.Surface) -> BaseScreen:
        self.current_scene = scene_name
        scene: BaseScreen
        match scene_name:
            case SceneTypes.MAIN_MENU:
                scene = MainMenuScreen(surface, self)
            case SceneTypes.SERVER_DOWN:
                scene = NoServerScreen(surface)
            case SceneTypes.SETTINGS:
                scene = SettingsScreen(surface, self)
            case SceneTypes.CREATE_LOBBY:
                scene = CreateLobbyScreen(surface, self)
            case SceneTypes.JOIN_LOBBY:
                scene = JoinLobbyScreen(surface, self)
            case SceneTypes.LOBBY:
                scene = LobbyScreen(surface, self)
            case SceneTypes.GAME:
                scene = GameScreen(surface, self)
            case SceneTypes.POST_GAME:
                scene = PostGameScreen(surface, self)
            case SceneTypes.TUTORIAL:
                # TODO: Replace the placeholder with the actual interactive tutorial
                scene = MessageScreen(surface, self, title="Tutorial", message="Coming soon")
            #Wenn keine vernünftige Scene übergeben wurde, tu nichts. Sollte nie passieren.
            case _:
                scene = MainMenuScreen(surface, self)
        
        return scene

    #Rendere den Screen in jedem Frame
    def update_screen(self, screen: BaseScreen, dt: float) -> None:
        screen.update(dt)
        screen.draw()
        pygame.display.flip()

    def sync_transport(self, surface: pygame.Surface) -> BaseScreen | None:
        next_scene: SceneTypes | None = None

        if self.transport_state.snapshot_version != self._seen_snapshot_version:
            self._seen_snapshot_version = self.transport_state.snapshot_version
            snapshot = self.transport_state.game_snapshot
            if snapshot is not None:
                self.display_state.apply_snapshot(snapshot)
                self.runtime_state.game.spare_rotation = 0
                self.runtime_state.clear_pending()
                self.runtime_state.clear_errors()
                next_scene = self._scene_from_snapshot()

        if self.transport_state.game_left_version != self._seen_game_left_version:
            self._seen_game_left_version = self.transport_state.game_left_version
            self.display_state.clear()
            self.runtime_state.game.spare_rotation = 0
            self.runtime_state.clear_pending()
            self.runtime_state.clear_errors()
            next_scene = SceneTypes.MAIN_MENU

        if self.transport_state.error_version != self._seen_error_version:
            self._seen_error_version = self.transport_state.error_version
            error = self.transport_state.last_error
            if error is not None:
                apply_server_error(self.runtime_state, error)

        if next_scene is None or next_scene == self.current_scene:
            return None
        return self.switch_scene(next_scene, surface)

    def _scene_from_snapshot(self) -> SceneTypes:
        if self.display_state.is_post_game:
            return SceneTypes.POST_GAME
        if self.display_state.is_game:
            return SceneTypes.GAME
        return SceneTypes.LOBBY
