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
from client.screens.menu.no_server_screen import NoServerScreen
from client.screens.menu.settings_screen import SettingsScreen
from client.screens.menu.stats_screen import StatsScreen
from client.screens.tutorial.tutorial_screen import TutorialPostGameScreen, TutorialScreen
from shared.types.enums import GamePhase

if TYPE_CHECKING:
    from client.screens.core.scene_manager import SceneManager

def create_screen(scene: SceneTypes, surface: pygame.Surface, manager: SceneManager) -> BaseScreen:
    """
    The factory is responsible for creating screens based on the current scene type.
    This is used in the SceneManager to create the appropriate screen when switching scenes.
    """
    match scene:
        case SceneTypes.MAIN_MENU:
            return MainMenuScreen(surface, manager)
        case SceneTypes.STATS:
            return StatsScreen(surface, manager)
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
            if (
                manager.tutorial_session is not None
                and manager.tutorial_session.snapshot is not None
                and manager.tutorial_session.snapshot.phase == GamePhase.POSTGAME
            ):
                return TutorialPostGameScreen(surface, manager)
            return PostGameScreen(surface, manager)
        case SceneTypes.TUTORIAL:
            return TutorialScreen(surface, manager)
