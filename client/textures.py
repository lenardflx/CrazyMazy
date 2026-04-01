from __future__ import annotations

import pygame

from shared.types.enums import PlayerColor, PlayerSkin, TreasureType
from shared.paths import BASE_DIR


def _image_load(path: str) -> pygame.Surface:
    """Load a pygame surface from the given path relative to the project base directory."""
    surface = pygame.image.load(BASE_DIR / path)
    if pygame.display.get_surface() is None:
        return surface
    return surface.convert_alpha()


PLAYER_IMAGES: dict[PlayerSkin, dict[PlayerColor, pygame.Surface]] = {
    PlayerSkin.DEFAULT: {
        PlayerColor.RED: _image_load("assets/images/players/default/red.png"),
        PlayerColor.BLUE: _image_load("assets/images/players/default/blue.png"),
        PlayerColor.GREEN: _image_load("assets/images/players/default/green.png"),
        PlayerColor.YELLOW: _image_load("assets/images/players/default/yellow.png"),
    },
}

TILE_IMAGES = {
    "STRAIGHT": _image_load("assets/images/tiles/straight.png"),
    "CORNER": _image_load("assets/images/tiles/corner.png"),
    "T": _image_load("assets/images/tiles/t_shape.png"),
}

UI_IMAGES = {
    "BUTTONS": _image_load("assets/images/ui/menu_button.png"),
    "TURN_ARROW": _image_load("assets/images/ui/turn_arrow.png"),
    "CLOSE": _image_load("assets/images/ui/close.png"),
    "TITLE_BACKGROUND": _image_load("assets/images/ui/titleBackground.png"),
    "TITLE_ANIMATION_0": _image_load("assets/images/ui/title-bg-0.png"),
    "TITLE_ANIMATION_1": _image_load("assets/images/ui/title-bg-1.png"),
    "TITLE_ANIMATION_2": _image_load("assets/images/ui/title-bg-2.png"),
    "SPACE_BACKGROUND": _image_load("assets/images/ui/backgroundSpace.png"),
}

TREASURE_IMAGES = {
    TreasureType.SKULL.value: _image_load("assets/images/treasures/skull.png"),
    TreasureType.SWORD.value: _image_load("assets/images/treasures/sword.png"),
    TreasureType.GOLDBAG.value: _image_load("assets/images/treasures/goldbag.png"),
    TreasureType.KEYS.value: _image_load("assets/images/treasures/keys.png"),
    TreasureType.EMERALD.value: _image_load("assets/images/treasures/emerald.png"),
    TreasureType.ARMOR.value: _image_load("assets/images/treasures/armor.png"),
    TreasureType.BOOK.value: _image_load("assets/images/treasures/book.png"),
    TreasureType.CROWN.value: _image_load("assets/images/treasures/crown.png"),
    TreasureType.CHEST.value: _image_load("assets/images/treasures/chest.png"),
    TreasureType.CANDLE.value: _image_load("assets/images/treasures/candle.png"),
    TreasureType.MAP.value: _image_load("assets/images/treasures/map.png"),
    TreasureType.RING.value: _image_load("assets/images/treasures/ring.png"),
    TreasureType.DRAGON.value: _image_load("assets/images/treasures/dragon.png"),
    TreasureType.GHOST.value: _image_load("assets/images/treasures/ghost.png"),
    TreasureType.BAT.value: _image_load("assets/images/treasures/bat.png"),
    TreasureType.GOBLIN.value: _image_load("assets/images/treasures/goblin.png"),
    TreasureType.PRINCESS.value: _image_load("assets/images/treasures/princess.png"),
    TreasureType.GENIE.value: _image_load("assets/images/treasures/genie.png"),
    TreasureType.BUG.value: _image_load("assets/images/treasures/bug.png"),
    TreasureType.OWL.value: _image_load("assets/images/treasures/owl.png"),
    TreasureType.LIZARD.value: _image_load("assets/images/treasures/lizard.png"),
    TreasureType.SPIDER.value: _image_load("assets/images/treasures/spider.png"),
    TreasureType.FLY.value: _image_load("assets/images/treasures/fly.png"),
    TreasureType.RAT.value: _image_load("assets/images/treasures/rat.png"),
}
