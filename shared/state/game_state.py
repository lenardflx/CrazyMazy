from enum import Enum
from shared.state.textures import *
from collections import deque
from shared.state.errors import TileError
from random import randint, shuffle


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
        # store tile metadata
        self.type = type
        self.orientation = orientation
        self._treasure = treasure

        # will be filled by load_texture()
        self.texture = None

        # path = [N, E, S, W]
        self.path = deque([0,0,0,0])

        # initialize path + texture based on type + orientation
        self.set_paths()

    def set_paths(self):
        # base path pattern for orientation NORTH
        if self.type == TileType.STRAIGHT.value:
            self.path = deque([1,0,1,0])  # N E S W
        elif self.type == TileType.CORNER.value:
            self.path = deque([1,1,0,0])
        elif self.type == TileType.T_PIECE.value:
            self.path = deque([1,1,0,1])
        else:
            # invalid tile type → fail fast
            raise TileError(f"Unbekannter Tile-Typ: '{self.type}'")

        # rotate path according to orientation
        self.path.rotate(TileOrientation(self.orientation).value)

        # convert to list for easier use elsewhere
        self.path = list(self.path)

    def load_texture(self):
        # lookup base texture from table
        texture = TILE_IMAGES[TileType(self.type).name]

        # rotate texture depending on orientation
        if self.orientation == TileOrientation.NORTH.value:
            self.texture = texture
        elif self.orientation == TileOrientation.EAST.value:
            self.texture = pygame.transform.rotate(texture, 270)
        elif self.orientation == TileOrientation.SOUTH.value:
            self.texture = pygame.transform.rotate(texture, 180)
        elif self.orientation == TileOrientation.WEST.value:
            self.texture = pygame.transform.rotate(texture, 90)

    def rotate_left(self):
        # rotate orientation counter‑clockwise
        self.orientation = (TileOrientation(self.orientation).value - 1) % 4

        # update texture + path
        self.load_texture()
        self.set_paths()

    def rotate_right(self):
        # rotate orientation clockwise
        self.orientation = (TileOrientation(self.orientation).value + 1) % 4

        # update texture + path
        self.load_texture()
        self.set_paths()


class Board:
    def __init__(self, width: int = 7):
        self.width = width # may at a scaling feature in the future
        self.tiles = {}

        # stack with moving tiles
        stack = [Tile(TileType.CORNER, TileOrientation(randint(0, 3))) for i in range(8)] # corner without treasures
        stack = [Tile(TileType.CORNER, TileOrientation(randint(0, 3)), TreasureType(i+22)) for i in range(5)] #corners with treasures
        stack += [Tile(TileType.T_PIECE, TileOrientation(randint(0, 3)), TreasureType(i+16)) for i in range(5)] # all t-pieces have treasures
        stack += [Tile(TileType.STRAIGHT, TileOrientation(randint(0, 1))) for i in range(12)] # straights dont have treasures
        self.stack = shuffle(stack)

    def create_board(self):
        treasure_order = [i+4 for i in range(12)]
        treasure_order.shuffle()
        counter = 0
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
                    self.tiles.update({(j,i) : Tile(TileType.T_PIECE, TileOrientation.EAST, TreasureType(treasure_order[counter]))})
                    counter += 1
                # bottom row
                elif i == self.width-1 and j%2==1 and 0<j>self.width-1:
                    self.tiles.update({(j, i): Tile(TileType.T_PIECE, TileOrientation.NORTH, TreasureType(treasure_order[counter]))})
                    counter += 1
                # left row
                elif j == 0 and i%2==1 and 0<i>self.width-1:
                    self.tiles.update({(j,i) : Tile(TileType.T_PIECE,TileOrientation.EAST, TreasureType(treasure_order[counter]))})
                    counter += 1
                # right row
                elif j == self.width-1 and i%2==1 and 0<i>self.width-1:
                    self.tiles.update({(j, i): Tile(TileType.T_PIECE, TileOrientation.WEST, TreasureType(treasure_order[counter]))})
                    counter += 1
                # middle
                elif i%2==1 and j%2==1:
                    self.tiles.update({(j,i) : Tile(TileType.T_PIECE, TileOrientation(randint(0,3)), TreasureType(treasure_order[counter]))})
                    counter += 1
                # rest
                else:
                    self.tiles.update({(j,i) : None})

    def fill_board(self):
        counter = 0
        for i in range(self.width):
            for j in range(self.width):
                if self.tiles[(j,i)] is None:
                    self.tiles.update({(j,i) : self.stack[counter]})
                    counter += 1

        self.tiles.update({"spare" : self.stack[counter]})