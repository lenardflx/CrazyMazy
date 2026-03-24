# Author: Christopher Ionescu

#from __future__ import annotations
import pygame
from client.screens.base_screen import BaseScreen
from client.screens.main_menu_screen import MainMenuScreen
from client.screens.no_server_screen import NoServerScreen

#ScreenManager, mit dem die Screens gewechselt werden können
class SceneManager:
    def __init__(self):
        self.current_scene = ""

    #Zeige die Correcte Scene
    def switch_scene(self, scene_name, surface) -> BaseScreen:
        scene = surface
        match scene_name:
            case "Main Menu":
                scene = MainMenuScreen(surface)
            case "Server Down":
                scene = NoServerScreen(surface)
            case "Settings":
                pass
            case "Create Lobby":
                pass
            case "Join Lobby":
                pass
            case "Start Game":
                pass
            #Wenn keine vernünftige Scene übergeben wurde, tu nichts
            case _:
                return surface
            
        self.current_scene = scene_name
        return scene

    #Rendere den Screen in jedem Frame
    def update_screen(self, screen, dt):
        
        screen.update(dt)
        screen.draw()
        pygame.display.flip()

