# Author: Lenard Felix

from __future__ import annotations

from enum import Enum

class SceneTypes(Enum):
    """Enum of all available scene types. The SceneManager uses these to determine which screen to create."""
    MAIN_MENU = "Main Menu"
    SERVER_DOWN = "Server Down"
    SETTINGS = "Settings"
    CREATE_LOBBY = "Create Lobby"
    JOIN_LOBBY = "Join Lobby"
    LOBBY = "Lobby"
    GAME = "Game"
    POST_GAME = "Post Game"
    TUTORIAL = "Tutorial"
