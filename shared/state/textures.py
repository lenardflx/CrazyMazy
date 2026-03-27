# Author: Lenard Felix

import pygame

from shared.models import TreasureType, PlayerColor, PlayerSkin
from shared.paths import BASE_DIR


def image_load(path: str) -> pygame.Surface:
    return pygame.image.load(BASE_DIR / path)


PLAYER_IMAGES: dict[PlayerSkin, dict[PlayerColor, pygame.Surface]] = {
    PlayerSkin.DEFAULT: {
        PlayerColor.RED:    image_load("assets/images/players/default/red.png"),
        PlayerColor.BLUE:   image_load("assets/images/players/default/blue.png"),
        PlayerColor.GREEN:  image_load("assets/images/players/default/green.png"),
        PlayerColor.YELLOW: image_load("assets/images/players/default/yellow.png"),
    },
}

TILE_IMAGES = {
    "STRAIGHT": image_load("assets/images/tiles/straight.png"),
    "CORNER":   image_load("assets/images/tiles/corner.png"),
    "T":        image_load("assets/images/tiles/t_shape.png"),
}

UI_IMAGES = {
    "BUTTONS":    image_load("assets/images/ui/menu_button.png"),
    "TURN_ARROW": image_load("assets/images/ui/turn_arrow.png"),
    "CLOSE":      image_load("assets/images/ui/close.png"),
}

# TODO: Replace placeholder treasure art with final assets once ready
TREASURE_IMAGES = {
    TreasureType.SKULL.value:    image_load("assets/images/treasures/skull.png"),
    TreasureType.SWORD.value:    image_load("assets/images/treasures/sword.png"),
    TreasureType.GOLDBAG.value:  image_load("assets/images/treasures/goldbag.png"),
    TreasureType.KEYS.value:     image_load("assets/images/treasures/keys.png"),
    TreasureType.EMERALD.value:  image_load("assets/images/treasures/emerald.png"),
    TreasureType.ARMOR.value:    image_load("assets/images/treasures/armor.png"),
    TreasureType.BOOK.value:     image_load("assets/images/treasures/book.png"),
    TreasureType.CROWN.value:    image_load("assets/images/treasures/crown.png"),
    TreasureType.CHEST.value:    image_load("assets/images/treasures/chest.png"),
    TreasureType.CANDLE.value:   image_load("assets/images/treasures/candle.png"),
    TreasureType.MAP.value:      image_load("assets/images/treasures/map.png"),
    TreasureType.RING.value:     image_load("assets/images/treasures/ring.png"),
    TreasureType.DRAGON.value:   image_load("assets/images/treasures/dragon.png"),
    TreasureType.GHOST.value:    image_load("assets/images/treasures/ghost.png"),
    TreasureType.BAT.value:      image_load("assets/images/treasures/bat.png"),
    TreasureType.GOBLIN.value:   image_load("assets/images/treasures/goblin.png"),
    TreasureType.PRINCESS.value: image_load("assets/images/treasures/princess.png"),
    TreasureType.GENIE.value:    image_load("assets/images/treasures/genie.png"),
    TreasureType.BUG.value:      image_load("assets/images/treasures/bug.png"),
    TreasureType.OWL.value:      image_load("assets/images/treasures/owl.png"),
    TreasureType.LIZARD.value:   image_load("assets/images/treasures/lizard.png"),
    TreasureType.SPIDER.value:   image_load("assets/images/treasures/spider.png"),
    TreasureType.FLY.value:      image_load("assets/images/treasures/fly.png"),
    TreasureType.RAT.value:      image_load("assets/images/treasures/rat.png"),
}
