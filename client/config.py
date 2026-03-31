# Author: Lenard Felix
 
"""
This file holds global configuration values for the client, such as window dimensions, server connection details and other constants.
Server connection is configured via the ".env" file. You can read how to set it up in the README.md.
"""

import os

WINDOW_TITLE = "Crazy Mazy"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60 # frames per second
MENU_BACKGROUND_ANIMATION_FRAMES = 3

SERVER_HOST: str = os.getenv("CLIENT_SERVER_HOST", "localhost")
SERVER_PORT: int = int(os.getenv("SERVER_PORT", "5555"))
