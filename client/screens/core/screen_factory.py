# Author: Lenard Felix

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

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

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager


def create_screen(scene: SceneTypes, surface: pygame.Surface, manager: SceneManager) -> BaseScreen:
    match scene:
        case SceneTypes.MAIN_MENU:
            return MainMenuScreen(surface, manager)
        case SceneTypes.SERVER_DOWN:
            return NoServerScreen(surface)
        case SceneTypes.SETTINGS:
            return SettingsScreen(surface, manager)
        case SceneTypes.CREATE_LOBBY:
            return CreateLobbyScreen(surface, manager)
        case SceneTypes.JOIN_LOBBY:
            return JoinLobbyScreen(surface, manager)
        case SceneTypes.LOBBY:
            return LobbyScreen(surface, manager)
        case SceneTypes.GAME:
            return GameScreen(surface, manager)
        case SceneTypes.POST_GAME:
            return PostGameScreen(surface, manager)
        case SceneTypes.TUTORIAL:
            # TODO: Replace with the actual interactive tutorial screen
            return MessageScreen(surface, manager, title="Tutorial", message="Coming soon")
