from shared.state.game_state import Tile, TileType
import pygame

def test_tile_texture():
    tile : Tile = Tile(TileType.CORNER, 0)
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    tile.load_texture()
    bild = tile.texture
    bild = pygame.transform.scale(bild, (400, 400))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(bild, (100, 100))
        pygame.display.flip()
    pygame.quit()


def test_tile_rotation():
    tile = Tile(1, 0)
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    tile.load_texture()

    bild = tile.texture
    bild = pygame.transform.scale(bild, (400, 400))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        screen.blit(bild, (100, 100))
        pygame.display.flip()

        pygame.time.wait(1000)

        tile.rotate_left()
        bild = pygame.transform.scale(tile.texture, (400, 400))

        screen.fill((0, 0, 0))
        screen.blit(bild, (100, 100))
        pygame.display.flip()

        pygame.time.wait(1000)

        tile.rotate_right()
        bild = pygame.transform.scale(tile.texture, (400, 400))

        screen.fill((0, 0, 0))
        screen.blit(bild, (100, 100))
        pygame.display.flip()

        pygame.time.wait(1000)

        tile.rotate_right()
        bild = pygame.transform.scale(tile.texture, (400, 400))

        screen.fill((0, 0, 0))
        screen.blit(bild, (100, 100))
        pygame.display.flip()

        pygame.time.wait(1000)

        tile.rotate_right()
        bild = pygame.transform.scale(tile.texture, (400, 400))

        screen.fill((0, 0, 0))
        screen.blit(bild, (100, 100))
        pygame.display.flip()

    pygame.quit()

def test_tile_paths():
    tile : Tile = Tile(0, 3)
    tile.set_paths()
    print(tile.path)
