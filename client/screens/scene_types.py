from __future__ import annotations

from enum import Enum


class SceneTypes(Enum):
    MAIN_MENU = "Main Menu"
    SERVER_DOWN = "Server Down"
    SETTINGS = "Settings"
    CREATE_LOBBY = "Create Lobby"
    JOIN_LOBBY = "Join Lobby"
    TUTORIAL = "Tutorial"
    START_GAME = "Start Game"
