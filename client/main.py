# Author: Lenard Felix, Christopher Ionescu

import pygame

from client.network.client_connection import ClientConnection
from client.config import FPS, SERVER_HOST, SERVER_PORT, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from client.screens.scene_manager import SceneManager, SceneTypes


def main() -> None:
    # Initialize Pygame and create the main window
    pygame.init()
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    # Connect to the server
    conn = ClientConnection()
    scene_manager = SceneManager()
    
    #Wenn eine Verbindung zum Server aufgebaut werden kann, gehe ins Hauptmenü, sonst zeige eine Fehlermeldung.
    connected = conn.connect(SERVER_HOST, SERVER_PORT)

    if connected:
        current_scene = SceneTypes.MAIN_MENU
    else:
        current_scene = SceneTypes.SERVER_DOWN

    screen = scene_manager.switch_scene(current_scene, surface)

    # Main game loop
    running = True
    while running:
        #Die Zeit des Frames in Sekunden
        dt = clock.tick(FPS) / 1000.0

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
