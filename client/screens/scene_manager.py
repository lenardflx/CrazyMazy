# Author: Christopher Ionescu

import pygame
from enum import Enum
from client.screens.base_screen         import BaseScreen
from client.screens.main_menu_screen    import MainMenuScreen
from client.screens.no_server_screen    import NoServerScreen
from client.screens.settings_screen     import SettingsScreen

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

        self.current_scene = SceneTypes.MAIN_MENU
        self.next_scene = SceneTypes.MAIN_MENU
        
    #Wechsle zur korrekten Scene
    def switch_scene(self, surface) -> BaseScreen:
        match self.next_scene:
            case SceneTypes.MAIN_MENU:
                sf = MainMenuScreen(surface, self)
            case SceneTypes.SERVER_DOWN:
                sf = NoServerScreen(surface)
            case SceneTypes.SETTINGS:
                sf = SettingsScreen(surface, self)
            case SceneTypes.CREATE_LOBBY:
                sf = MainMenuScreen(surface, self)
            case SceneTypes.JOIN_LOBBY:
                sf = MainMenuScreen(surface, self)
            case SceneTypes.START_GAME:
                sf = MainMenuScreen(surface, self)
            #Wenn keine vernünftige Scene übergeben wurde, gehe ins Hauptmenü. Sollte nie passieren.
            case _:
                sf = MainMenuScreen(surface, self)
        
        return sf
    
    def set_next_scene(self, scene_name: SceneTypes):
        self.next_scene = scene_name

    #Rendere den Screen in jedem Frame
    def update_screen(self, screen, surface, dt):
        #Falls der Screen geändert wurde, wechsle zum neuen Screen
        if self.current_scene != self.next_scene:
            screen = self.switch_scene(surface)
            self.current_scene = self.next_scene
        screen.update(dt)
        screen.draw()

        pygame.display.flip()
        pygame.display.update()

        return screen

