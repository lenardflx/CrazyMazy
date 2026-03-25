from enum import Enum
from shared.state.textures import *
from collections import deque
from shared.state.errors import TileError, BoardError
from random import randint, shuffle
from typing import Tuple


class GameState:
    def __init__(self, game):
        pass

class TileType(Enum):
    STRAIGHT = 0
    T_PIECE = 1
    CORNER = 2
    WALL = 3

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
        self.treasure = treasure

        # will be filled by load_texture()
        self.texture = None

        # path = [N, E, S, W]
        self.path = deque([0,0,0,0])

        # initialize path + texture based on type + orientation
        self.set_paths()

    def set_paths(self):
        # base path pattern for orientation NORTH
        if self.type == TileType.STRAIGHT:
            self.path = deque([1,0,1,0])  # N E S W
        elif self.type == TileType.CORNER:
            self.path = deque([1,1,0,0])
        elif self.type == TileType.T_PIECE:
            self.path = deque([1,1,0,1])
        elif self.type == TileType.WALL:
            self.path = deque([0,0,0,0])
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
        self.spare = None

        # stack with moving tiles
        stack = [Tile(TileType.CORNER, TileOrientation(randint(0, 3))) for i in range(9)] # corner without treasures
        stack += [Tile(TileType.CORNER, TileOrientation(randint(0, 3)), TreasureType(i+22)) for i in range(6)] #corners with treasures
        stack += [Tile(TileType.T_PIECE, TileOrientation(randint(0, 3)), TreasureType(i+16)) for i in range(6)] # all t-pieces have treasures
        stack += [Tile(TileType.STRAIGHT, TileOrientation(randint(0, 1))) for i in range(13)] # straights don't have treasures
        shuffle(stack)
        self.stack = stack

    def get_neighbour(self, position: Tuple[int, int], direction: TileOrientation) -> Tuple[int, int]:
        # position on border => no neighbor
        if position[1] == 0 and direction == TileOrientation.NORTH:
            return None
        if position[1] == self.width - 1 and direction == TileOrientation.SOUTH:
            return None
        if position[0] == 0 and direction == TileOrientation.WEST:
            return None
        if position[0] == self.width - 1 and direction == TileOrientation.EAST:
            return None

        # return neighbour
        if direction == TileOrientation.NORTH:
            return position[0], position[1]-1
        if direction == TileOrientation.EAST:
            return position[0]+1, position[1]
        if direction == TileOrientation.SOUTH:
            return position[0], position[1]+1
        if direction == TileOrientation.WEST:
            return position[0]-1, position[1]

    def move_possible(self, position: Tuple[int, int], direction: TileOrientation):
        # wall on tile your standing on
        if self.tiles[position].path[direction.value] == 0:
            return False

        # end of board
        if self.get_neighbour(position, direction) == None:
            return False

        # wall of neighbour in your way
        if self.tiles[self.get_neighbour(position, direction)].path[(direction.value+2)%4] == 0:
            return False


        return True

    def pathvalidating(self, start_position: Tuple[int, int], end_position: Tuple[int, int]):
        return (end_position in self.pathfind(start_position))


    def pathfind(self, position: Tuple[int, int], visited=[]):
        # Add the current position to the visited list
        visited.append(position)

        # Explore all 4 possible directions (0–3)
        for d in range(4):
            # Check if movement in direction d is allowed AND the neighbour exists
            neighbour = self.get_neighbour(position, TileOrientation(d))
            if self.move_possible(position, TileOrientation(d)) and neighbour not in visited:
                # Recursively continue pathfinding from the neighbour
                # The recursive call mutates 'visited' in place, so no reassignment is needed
                self.pathfind(neighbour, visited)

        # Return the accumulated list of visited positions
        return visited

    def create_board(self):
        treasure_order = [i+4 for i in range(12)]
        shuffle(treasure_order)
        counter = 0
        for i in range(self.width):
            for j in range(self.width):
                # top left corner
                if i==0 and j==0:
                    self.tiles.update({(j,i) : Tile(TileType.CORNER, TileOrientation.EAST, TreasureType.YELLOW)})
                # top right corner
                elif i == 0 and j == self.width-1:
                    self.tiles.update({(j, i): Tile(TileType.CORNER, TileOrientation.SOUTH, TreasureType.BLUE)})
                # bottom left corner
                elif i == self.width-1 and j == 0:
                    self.tiles.update({(j, i): Tile(TileType.CORNER, TileOrientation.NORTH, TreasureType.RED)})
                # bottom right corner
                elif i == self.width-1 and j == self.width-1:
                    self.tiles.update({(j, i): Tile(TileType.CORNER, TileOrientation.WEST, TreasureType.GREEN)})

                # top row
                elif i == 0 and j%2==0 and 0<j>self.width-1:
                    self.tiles.update({(j,i) : Tile(TileType.T_PIECE, TileOrientation.EAST, TreasureType(treasure_order[counter]))})
                    counter += 1
                # bottom row
                elif i == self.width-1 and j%2==0 and 0<j>self.width-1:
                    self.tiles.update({(j, i): Tile(TileType.T_PIECE, TileOrientation.NORTH, TreasureType(treasure_order[counter]))})
                    counter += 1
                # left row
                elif j == 0 and i%2==0 and 0<i>self.width-1:
                    self.tiles.update({(j,i) : Tile(TileType.T_PIECE,TileOrientation.EAST, TreasureType(treasure_order[counter]))})
                    counter += 1
                # right row
                elif j == self.width-1 and i%2==0 and 0<i>self.width-1:
                    self.tiles.update({(j, i): Tile(TileType.T_PIECE, TileOrientation.WEST, TreasureType(treasure_order[counter]))})
                    counter += 1
                # middle
                elif i%2==0 and j%2==0:
                    self.tiles.update({(j,i) : Tile(TileType.T_PIECE, TileOrientation(randint(0,3)), TreasureType(treasure_order[counter]))})
                    counter += 1
                # rest
                else:
                    self.tiles.update({(j,i) : None})

    def create_blocked_board(self):
        for i in range(self.width):
            for j in range(self.width):
                self.tiles.update({(j,i) : Tile(TileType.WALL, TileOrientation.NORTH)})

    def change_tile(self, x : int, y : int, tile):
        self.tiles.update({(x,y) : tile})

    def fill_board(self):
        counter = 0
        for i in range(self.width):
            for j in range(self.width):
                if self.tiles[(j,i)] is None:
                    self.tiles.update({(j,i) : self.stack[counter]})
                    counter += 1
        self.spare = self.stack[counter]

    def print_board(self):
        board = self._randomBoard()
        for i in range(board.width):
            for j in range(board.width):
                if board.tiles[(j, i)] is not None:
                    print("1")
                else:
                    print("0")
            print("\n")

    def insert_tile(self, x, y):
        # check if tile is inserted at the border
        if (x != 0 and y != 0) and (x != self.width-1 and y != self.width-1):
            raise BoardError("You can't insert a tile in the middle")
        # check if the tile is placed outside the board
        if (x<0 or x>=self.width) or (y<0 or y>=self.width):
            raise BoardError("You can't insert a tile outside the board")
        # check if tile is movable
        if x % 2 == 0 and y % 2 == 0:
            raise BoardError("That tile isn't movable")

        # horizontal from the left
        if x == 0:
            for i in range(self.width):
                ram = self.tiles[(i,y)]
                self.tiles.update({(i,y) : self.spare})
                self.spare = ram
        #horizontal from the right
        if x == self.width-1:
            for i in range(self.width-1, -1, -1):
                ram = self.tiles[(i,y)]
                self.tiles.update({(i,y) : self.spare})
                self.spare = ram

        # vertical from the top
        if y == 0:
            for i in range(self.width):
                ram = self.tiles[(x, i)]
                self.tiles.update({(x, i) : self.spare})
                self.spare = ram
        # vertical from the bottom
        if y == self.width-1:
            for i in range(self.width-1, -1, -1):
                ram = self.tiles[(x, i)]
                self.tiles.update({(x, i) : self.spare})
                self.spare = ram