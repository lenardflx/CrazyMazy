import pygame
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

def image_load(path):
    return pygame.image.load(BASE_DIR / path)


TILE_IMAGES = {
    "STRAIGHT": image_load("assets/images/tiles/straight.png"),
    "CORNER": image_load("assets/images/tiles/corner.png"),
    "T_PIECE": image_load("assets/images/tiles/t_shape.png"),
    "BUTTONS": image_load("assets/images/Buttons_and_UI/PlaceholderMenuButton.png")
}