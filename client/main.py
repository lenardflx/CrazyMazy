# Author: Lenard Felix, Christopher Ionescu

"""
This is the main entry point of the client application.
It initializes the Pygame window, connects to the server, and holds the main game loop.
"""

import pygame

import client.network.handlers # Unused import, but needed for the handlers to load

from client.sound.manager import AudioManager
from client.config import FPS, SERVER_HOST, SERVER_PORT, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from client.network.client_connection import ClientConnection
from client.network.state import ClientState
from client.screens.core.scene_manager import SceneManager, SceneTypes
from client.textures import UI_IMAGES


def main() -> None:
    # Initialize Pygame
    pygame.init()

    # Load Application Icon
    icon = UI_IMAGES["ICON"]
    pygame.display.set_icon(icon)

    # Create the main window
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    # Connect to the server
    conn = ClientConnection()
    state = ClientState()
    audio = AudioManager()
    scene_manager = SceneManager(conn, state, surface, audio)
    
    # Try to connect to the server and set the initial scene based on the connection result
    print(f"Connecting to server at {SERVER_HOST}:{SERVER_PORT}...")
    connected = conn.connect(SERVER_HOST, SERVER_PORT)
    if connected:
        current_scene = SceneTypes.MAIN_MENU
        print("Connected to server successfully.")
    else:
        current_scene = SceneTypes.SERVER_DOWN

    if scene_manager.client_settings.fullscreen:
        scene_manager.apply_fullscreen(True)

    scene_manager.go_to(current_scene)

    # Main game loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # Poll the server for incoming messages
        conn.poll(state)

        # Check if the server sent an update that requires a scene change
        scene_manager.sync_transport()

        # Handle Pygame events
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False
            else:
                scene_manager.handle_event(event)

        # Run the renderer for the current screen
        scene_manager.tick(dt)
    
    scene_manager.client_settings.write_JSON()

    conn.disconnect()
    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Client interrupted by user. Exiting...")
