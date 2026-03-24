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

class Tile:
    def __init__(self, type: TileType, orientation: TileOrientation, treasure: None | TreasureType = None):
        self.type = type
        self.orientation = orientation
        self._treasure = treasure

class Board:
    def __init__(self, width: int):
        self.width = width
        self.tiles = {}

    def create_board(self):
        for i in range(self.width):
            for j in range(self.width):
                # topleft corner
                if i==0 and j==0:
                    self.tiles.update({(j,i) : Tile(2, 1, 0)})
                # topright corner
                if i == 0 and j == self.width-1:
                    self.tiles.update({(j, i): Tile(2, 2, 1)})
                # bottomeft corner
                if i == self.width-1 and j == 0:
                    self.tiles.update({(j, i): Tile(2, 0, 2)})
                # bottomeft corner
                if i == self.width-1 and j == self.width-1:
                    self.tiles.update({(j, i): Tile(2, 3, 3)})

                # top row
                if i == 0 and j%2==1 and 0<j>self.width-1:
                    self.tiles.update({(j,i) : Tile(1, 2)})
                # bottom row
                elif i == self.width-1 and j%2==1 and 0<j>self.width-1:
                    self.tiles.update({(j, i): Tile(1, 0)})
                # left row
                elif j == 0 and i%2==1 and 0<i>self.width-1:
                    self.tiles.update({(j,i) : Tile(1,1)})
                # right row
                elif j == self.width-1 and i%2==1 and 0<i>self.width-1:
                    self.tiles.update({(j, i): Tile(1, 3)})
                # middle
                elif i%2==1 and j%2==1:
                    self.tiles.update({(j,i) : Tile(1, randint(0,3))})
                # rest
                else:
                    self.tiles.update({(j,i) : None})

    def fill_board(self):
        stack = [Tile(2, randint(0,3)) for i in range(14)]
        stack += [Tile(1, randint(0,3)) for i in range(5)]
        stack += [Tile(0, randint(0,1)) for i in range(12)]
        stack.shuffle()

        for i in range(self.width):
            for j in range(self.width):
                if self.tiles[(j,i)] == None:
                    self.tiles.update({(j,i) : stack[0]})
                    stack = stack[1:]

        self.tiles.update({"spare" : stack[0]})