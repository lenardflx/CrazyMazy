from pathlib import Path

import pygame

from shared.models import TreasureType

BASE_DIR = Path(__file__).resolve().parents[2]


def image_load(path: str) -> pygame.Surface:
    return pygame.image.load(BASE_DIR / path)


TILE_IMAGES = {
    "STRAIGHT": image_load("assets/images/tiles/straight.png"),
    "CORNER": image_load("assets/images/tiles/corner.png"),
    "T": image_load("assets/images/tiles/t_shape.png"),
}

UI_IMAGES = {
    "BUTTONS": image_load("assets/images/buttons_ui/PlaceholderMenuButton.png"),
}

# TODO: Replace the placeholder treasure art with the final assets once they are ready
TREASURE_IMAGES = {
    TreasureType.SKULL.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder1.png"),
    TreasureType.SWORD.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder2.png"),
    TreasureType.GOLDBAG.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder3.png"),
    TreasureType.KEYS.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder4.png"),
    TreasureType.EMERALD.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder5.png"),
    TreasureType.ARMOR.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder6.png"),
    TreasureType.BOOK.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder7.png"),
    TreasureType.CROWN.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder8.png"),
    TreasureType.CHEST.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder9.png"),
    TreasureType.CANDLE.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder10.png"),
    TreasureType.MAP.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder11.png"),
    TreasureType.RING.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder12.png"),
    TreasureType.DRAGON.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder13.png"),
    TreasureType.GHOST.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder14.png"),
    TreasureType.BAT.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder15.png"),
    TreasureType.GOBLIN.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder16.png"),
    TreasureType.PRINCESS.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder17.png"),
    TreasureType.GENIE.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder18.png"),
    TreasureType.BUG.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder19.png"),
    TreasureType.OWL.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder20.png"),
    TreasureType.LIZARD.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder21.png"),
    TreasureType.SPIDER.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder22.png"),
    TreasureType.FLY.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder23.png"),
    TreasureType.RAT.value: image_load("assets/images/treasure_placeholder/TreasurePlaceholder24.png"),
}
