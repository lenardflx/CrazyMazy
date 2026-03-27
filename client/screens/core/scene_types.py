# Author: Lenard Felix

from __future__ import annotations

from enum import Enum

#Eine Lookup-Liste aller Scenes
class SceneTypes(Enum):
    MAIN_MENU = "Main Menu"
    SERVER_DOWN = "Server Down"
    SETTINGS = "Settings"
    CREATE_LOBBY = "Create Lobby"
    JOIN_LOBBY = "Join Lobby"
    LOBBY = "Lobby"
    GAME = "Game"
    POST_GAME = "Post Game"
    TUTORIAL = "Tutorial"
