# Author: Lenard Felix, Christopher Ionescu

import pygame

import client.network.handlers
from client.config import FPS, SERVER_HOST, SERVER_PORT, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from client.network.client_connection import ClientConnection
from client.network.state import ClientState
from client.screens.core.scene_manager import SceneManager
from client.screens.core.scene_types import SceneTypes


def main() -> None:
    # Initialize Pygame and create the main window
    pygame.init()
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    # Connect to the server
    conn = ClientConnection()
    state = ClientState()
    scene_manager = SceneManager(conn, state)
    
    #Wenn eine Verbindung zum Server aufgebaut werden kann, gehe ins Hauptmenü, sonst zeige eine Fehlermeldung.
    if conn.connect(SERVER_HOST, SERVER_PORT):
        current_scene = SceneTypes.MAIN_MENU
    else:
        current_scene = SceneTypes.SERVER_DOWN

    screen = scene_manager.switch_scene(current_scene, surface)

    # Main game loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        conn.poll(state)
        next_screen = scene_manager.sync_transport(surface)
        if next_screen is not None:
            screen = next_screen

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False
            else:
                next_screen = screen.handle_event(event)
                if next_screen is not None:
                    screen = next_screen

        scene_manager.update_screen(screen, dt)

    conn.disconnect()
    pygame.quit()


if __name__ == "__main__":
    main()
