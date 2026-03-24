import pygame
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def image_load(path):
    return pygame.image.load(BASE_DIR / path)

CORNER = image_load("../../assets/images/tiles/corner.png")
T_PIECE = image_load("../../assets/images/tiles/t_shape.png")
STRAIGHT = image_load("../../assets/images/tiles/straight.png")

TILE_IMAGES = {
    "STRAIGHT": STRAIGHT,
    "CORNER": CORNER,
    "T_PIECE": T_PIECE
}