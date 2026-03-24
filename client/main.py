# Author: Lenard Felix, Christopher Ionescu

import pygame

import client.network.handlers
from client.config import FPS, SERVER_HOST, SERVER_PORT, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from client.network.client_connection import ClientConnection
from client.network.state import ClientState
from client.screens.scene_manager import SceneManager


def main() -> None:
    # Initialize Pygame and create the main window
    pygame.init()
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    # Connect to the server
    conn = ClientConnection()
    state = ClientState()
    scene_manager = SceneManager()

    # If the server is reachable, enter the main menu, otherwise show the server-down scene.
    current_scene = "Main Menu" if conn.connect(SERVER_HOST, SERVER_PORT) else "Server Down"
    screen = scene_manager.switch_scene(current_scene, surface)

    # Main game loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        conn.poll(state)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                screen.handle_event(event)

        scene_manager.update_screen(screen, dt)

    conn.disconnect()
    pygame.quit()


if __name__ == "__main__":
    main()
