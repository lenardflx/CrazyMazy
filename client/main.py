# Author: Lenard Felix

import pygame

from client.network.client_connection import ClientConnection
from client.screens.base_screen import BaseScreen
from client.screens.main_menu_screen import MainMenuScreen
from client.screens.no_server_screen import NoServerScreen
from client.config import FPS, SERVER_HOST, SERVER_PORT, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH


def main() -> None:
    # Initialize Pygame and create the main window
    pygame.init()
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    # Connect to the server
    conn = ClientConnection()

    # Choose the initial screen based on whether the connection was successful
    screen: BaseScreen = (
        MainMenuScreen(surface) if conn.connect(SERVER_HOST, SERVER_PORT)
        else NoServerScreen(surface)
    )

    # Main game loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                screen.handle_event(event)

        screen.update(dt)
        screen.draw()
        pygame.display.flip()

    conn.disconnect()
    pygame.quit()


if __name__ == "__main__":
    main()
