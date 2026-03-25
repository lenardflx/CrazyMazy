import pygame
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

def image_load(path):
    return pygame.image.load(BASE_DIR / path)


TILE_IMAGES = {
    "STRAIGHT": image_load("assets/images/tiles/straight.png"),
    "CORNER": image_load("assets/images/tiles/corner.png"),
    "T_PIECE": image_load("assets/images/tiles/t_shape.png")
}

TREASURES = {
    "ph1": image_load("assets/images/treasure_placeholder/TreasurePlaceholder1.png"),
    "ph2": image_load("assets/images/treasure_placeholder/TreasurePlaceholder2.png"),
    "ph3": image_load("assets/images/treasure_placeholder/TreasurePlaceholder3.png"),
    "ph4": image_load("assets/images/treasure_placeholder/TreasurePlaceholder4.png"),
    "ph5": image_load("assets/images/treasure_placeholder/TreasurePlaceholder5.png"),
    "ph6": image_load("assets/images/treasure_placeholder/TreasurePlaceholder6.png"),
    "ph7": image_load("assets/images/treasure_placeholder/TreasurePlaceholder7.png"),
    "ph8": image_load("assets/images/treasure_placeholder/TreasurePlaceholder8.png"),
    "ph9": image_load("assets/images/treasure_placeholder/TreasurePlaceholder9.png"),
    "ph10": image_load("assets/images/treasure_placeholder/TreasurePlaceholder10.png"),
    "ph11": image_load("assets/images/treasure_placeholder/TreasurePlaceholder11.png"),
    "ph12": image_load("assets/images/treasure_placeholder/TreasurePlaceholder12.png"),
    "ph13": image_load("assets/images/treasure_placeholder/TreasurePlaceholder13.png"),
    "ph14": image_load("assets/images/treasure_placeholder/TreasurePlaceholder14.png"),
    "ph15": image_load("assets/images/treasure_placeholder/TreasurePlaceholder15.png"),
    "ph16": image_load("assets/images/treasure_placeholder/TreasurePlaceholder16.png"),
    "ph17": image_load("assets/images/treasure_placeholder/TreasurePlaceholder17.png"),
    "ph18": image_load("assets/images/treasure_placeholder/TreasurePlaceholder18.png"),
    "ph19": image_load("assets/images/treasure_placeholder/TreasurePlaceholder19.png"),
    "ph20": image_load("assets/images/treasure_placeholder/TreasurePlaceholder20.png"),
    "ph21": image_load("assets/images/treasure_placeholder/TreasurePlaceholder21.png"),
    "ph22": image_load("assets/images/treasure_placeholder/TreasurePlaceholder22.png"),
    "ph23": image_load("assets/images/treasure_placeholder/TreasurePlaceholder23.png"),
    "ph24": image_load("assets/images/treasure_placeholder/TreasurePlaceholder24.png"),
}
