# Author: Christopher Ionescu

import pygame
from enum import Enum
from client.screens.base_screen import BaseScreen
from client.screens.main_menu_screen import MainMenuScreen
from client.screens.no_server_screen import NoServerScreen

#Die Scenes, die erlaubt sind
class SceneTypes(Enum):
    MAIN_MENU       = "Main Menu"
    SERVER_DOWN     = "Server Down"
    SETTINGS        = "Settings"
    CREATE_LOBBY    = "Create Lobby"
    JOIN_LOBBY      = "Join Lobby"
    START_GAME      = "Start Game"

#ScreenManager, mit dem die Screens gewechselt werden können
class SceneManager:
    def __init__(self):
        self.current_scene = ""

    #Wechsle zur korrekten Scene
    def switch_scene(self, scene_name: SceneTypes, surface) -> BaseScreen:
        scene = surface
        match scene_name:
            case SceneTypes.MAIN_MENU:
                scene = MainMenuScreen(surface)
            case SceneTypes.SERVER_DOWN:
                scene = NoServerScreen(surface)
            case SceneTypes.SETTINGS:
                pass
            case SceneTypes.CREATE_LOBBY:
                pass
            case SceneTypes.JOIN_LOBBY:
                pass
            case SceneTypes.START_GAME:
                pass
            #Wenn keine vernünftige Scene übergeben wurde, tu nichts. Sollte nie passieren.
            case _:
                return surface
        
        #Speichere, in welcher Scene wir gerade sind
        self.current_scene = scene_name
        return scene

    #Rendere den Screen in jedem Frame
    def update_screen(self, screen, dt):
        
        screen.update(dt)
        screen.draw()
        pygame.display.flip()
        pygame.display.update()

