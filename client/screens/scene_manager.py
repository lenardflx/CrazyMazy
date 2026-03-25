from __future__ import annotations

import pygame

from client.settings import ClientSettings
from client.screens.base_screen import BaseScreen
from client.screens.main_menu_screen import MainMenuScreen
from client.screens.message_screen import MessageScreen
from client.screens.no_server_screen import NoServerScreen
from client.screens.scene_types import SceneTypes
from client.screens.settings_screen import SettingsScreen

#ScreenManager, mit dem die Screens gewechselt werden können
class SceneManager:
    def __init__(self) -> None:
        self.current_scene: SceneTypes | None = None
        self.client_settings = ClientSettings()

    #Wechsle zur korrekten Scene
    def switch_scene(self, scene_name: SceneTypes, surface: pygame.Surface) -> BaseScreen:
        self.current_scene = scene_name
        match scene_name:
            case SceneTypes.MAIN_MENU:
                scene = MainMenuScreen(surface, self)
            case SceneTypes.SERVER_DOWN:
                scene = NoServerScreen(surface)
            case SceneTypes.SETTINGS:
                scene = SettingsScreen(surface, self)
            case SceneTypes.CREATE_LOBBY:
                scene = MessageScreen(surface, self, title="Create Lobby", message="Coming soon")
            case SceneTypes.JOIN_LOBBY:
                scene = MessageScreen(surface, self, title="Join Lobby", message="Coming soon")
            case SceneTypes.TUTORIAL:
                scene = MessageScreen(surface, self, title="Tutorial", message="Coming soon")
            case SceneTypes.START_GAME:
                scene = MainMenuScreen(surface, self)
            #Wenn keine vernünftige Scene übergeben wurde, tu nichts. Sollte nie passieren.
            case _:
                scene = MainMenuScreen(surface, self)
        
        return scene

    #Rendere den Screen in jedem Frame
    def update_screen(self, screen: BaseScreen, dt: float) -> None:
        screen.update(dt)
        screen.draw()
        pygame.display.flip()
