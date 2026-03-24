from enum import Enum


class GameState:
    def __init__(self, game):
        pass

class TileType(Enum):
    STRAIGHT = 0
    T_PIECE = 1
    CORNER = 2

class TileOrientation(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

class TreasureType(Enum):
    STAR = 0
    FROG = 1

class Tile:
    def __init__(self, type: TileType, orientation: TileOrientation, treasure: None | TreasureType = None):
        self.type = type
        self.orientation = orientation
        self._treasure = treasure

class Board:
    def __init__(self, width: int):
        self.width = width
        self.tiles = {}


