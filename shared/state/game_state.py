from enum import Enum
from random import randint


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
    YELLOW = 0
    BLUE = 1
    RED = 2
    GREEN = 3

    SKULL = 4
    SWORD = 5
    GOLDBAG = 6
    KEYS = 7
    EMERALD = 8
    ARMOR = 9
    BOOK = 10
    CROWN = 11
    CHEST = 12
    CANDLE = 13
    MAP = 14
    RING = 15
    DRAGON = 16
    GHOST = 17
    BAT = 18
    GOBLIN = 19
    PRINCESS = 20
    GENIE =  21
    BUG = 22
    OWL = 23
    LIZARD = 24
    SPIDER = 25
    FLY =  26
    RAT =  27

class Tile:
    def __init__(self, type: TileType, orientation: TileOrientation, treasure: None | TreasureType = None):
        self.type = type
        self.orientation = orientation
        self._treasure = treasure

class Board:
    def __init__(self, width: int):
        if width % 2 == 1:
            self.width = width
        else:
            self.width = width + 1
        self.tiles = {}

    def create_board(self):
        for i in range(self.width):
            for j in range(self.width):
                # top left corner
                if i==0 and j==0:
                    self.tiles.update({(j,i) : Tile(TileType.CORNER, TileOrientation.EAST, TreasureType.YELLOW)})
                # top right corner
                if i == 0 and j == self.width-1:
                    self.tiles.update({(j, i): Tile(TileType.CORNER, TileOrientation.SOUTH, TreasureType.BLUE)})
                # bottom left corner
                if i == self.width-1 and j == 0:
                    self.tiles.update({(j, i): Tile(TileType.CORNER, TileOrientation.NORTH, TreasureType.RED)})
                # bottom right corner
                if i == self.width-1 and j == self.width-1:
                    self.tiles.update({(j, i): Tile(TileType.CORNER, TileOrientation.WEST, TreasureType.GREEN)})

                # top row
                if i == 0 and j%2==1 and 0<j>self.width-1:
                    self.tiles.update({(j,i) : Tile(TileType.T_PIECE, TileOrientation.EAST)})
                # bottom row
                elif i == self.width-1 and j%2==1 and 0<j>self.width-1:
                    self.tiles.update({(j, i): Tile(TileType.T_PIECE, TileOrientation.NORTH)})
                # left row
                elif j == 0 and i%2==1 and 0<i>self.width-1:
                    self.tiles.update({(j,i) : Tile(TileType.T_PIECE,TileOrientation.EAST)})
                # right row
                elif j == self.width-1 and i%2==1 and 0<i>self.width-1:
                    self.tiles.update({(j, i): Tile(TileType.T_PIECE, TileOrientation.WEST)})
                # middle
                elif i%2==1 and j%2==1:
                    self.tiles.update({(j,i) : Tile(TileType.T_PIECE, TileOrientation(randint(0,3)))})
                # rest
                else:
                    self.tiles.update({(j,i) : None})

    def fill_board(self):
        stack = [Tile(TileType.CORNER, TileOrientation(randint(0,3))) for i in range(14)]
        stack += [Tile(TileType.T_PIECE, TileOrientation(randint(0,3))) for i in range(5)]
        stack += [Tile(TileType.STRAIGHT, TileOrientation(randint(0,1))) for i in range(12)]
        stack.shuffle()

        for i in range(self.width):
            for j in range(self.width):
                if self.tiles[(j,i)] is None:
                    self.tiles.update({(j,i) : stack[0]})
                    stack = stack[1:]

        self.tiles.update({"spare" : stack[0]})