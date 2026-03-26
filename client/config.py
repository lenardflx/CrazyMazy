# Author: Lenard Felix
 
import os

WINDOW_TITLE = "Crazy Mazy"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

SERVER_HOST: str = os.getenv("CLIENT_SERVER_HOST", "localhost")
SERVER_PORT: int = int(os.getenv("CLIENT_SERVER_PORT", "5555"))
