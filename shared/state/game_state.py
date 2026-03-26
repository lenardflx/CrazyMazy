# Author: Lennart William Owen, Raphael Eiden, Sarah Trapp, Lenard Felix
 
from collections import deque
from enum import Enum
from shared.state.errors import BoardError
from random import randint, shuffle
from typing import Tuple
import pygame
from shared.state.textures import TILE_IMAGES

# IMPORTANT: most of this should now be covered by models.py and the board lib. At least as a temporary solution that however works with the codebase

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
        """
        Represents a single tile on the board.

        Args:
            type: The structural tile type (STRAIGHT, CORNER, T_PIECE, WALL(just for testing)).
            orientation: The current rotation of the tile (NORTH/EAST/SOUTH/WEST).
            treasure: Optional treasure placed on this tile.
        """

        # Basic tile metadata
        self.type = type
        self.orientation = orientation
        self.treasure = treasure

        # Will hold the rotated pygame.Surface after load_texture()
        self.texture = None

        # Path connectivity in order [N, E, S, W]
        # Example: [1,0,1,0] means open to North + South
        self.path = None

        # Compute initial path layout based on type + orientation
        self.set_paths()

    def set_paths(self):
        """
        Computes the tile's connectivity (open paths) based on its type and orientation.

        Base patterns are defined for NORTH orientation.
        Then we rotate the deque to match the actual orientation.
        """

        # base path pattern for orientation NORTH
        parse_Tiletype = {TileType.STRAIGHT: [1,0,1,0], # N E S W
                          TileType.CORNER : [1,1,0,0],
                          TileType.T_PIECE : [1,1,0,1],
                          TileType.WALL : [0,0,0,0]}
        # set exit values for path
        path = deque(parse_Tiletype[self.type])


        # Rotate the connectivity pattern according to orientation
        # TileOrientation.value is 0=N, 1=E, 2=S, 3=W
        path.rotate(TileOrientation(self.orientation).value)

        # Convert deque → list for easier use elsewhere
        self.path = list(path)

    def load_texture(self):
        """
        Loads the base texture for this tile type and rotates it to match orientation.

        The TILE_IMAGES table stores unrotated (NORTH-facing) textures.
        """

        # Fetch base NORTH-facing texture
        texture = TILE_IMAGES[TileType(self.type).name]
        # get degree values for rotation of every orientation
        parse_orientation = {TileOrientation.NORTH : 0,
                          TileOrientation.EAST : 270,
                          TileOrientation.SOUTH : 180,
                          TileOrientation.WEST : 90}

        # Rotate depending on orientation
        # Note: pygame rotates counter-clockwise, so EAST = 270° etc.
        self.texture = pygame.transform.rotate(texture, parse_orientation[self.orientation])

    def rotate_left(self):
        """
        Rotates the tile 90° counter-clockwise.

        Updates:
        - orientation
        - path connectivity
        (Texture is NOT updated here; caller must call load_texture())
        """

        # Decrease orientation index modulo 4
        self.orientation = (TileOrientation(self.orientation).value - 1) % 4

        # Recompute connectivity
        self.set_paths()

    def rotate_right(self):
        """
        Rotates the tile 90° clockwise.

        Updates:
        - orientation
        - path connectivity
        (Texture is NOT updated here; caller must call load_texture())
        """

        # Increase orientation index modulo 4
        self.orientation = (TileOrientation(self.orientation).value + 1) % 4

        # Recompute connectivity
        self.set_paths()

class Board:
    def __init__(self, width: int):
        """
        Represents the full game board.

        Args:
            width: Board dimension (Labyrinth uses 7×7).
        """
        if width >= 7 and width % 2 == 1:
            self.width = width
        else:
            self.width = 7
        self.tiles = {}     # (x, y) → Tile
        self.spare = None   # tile currently outside the board

        # lenght of stack
        stack_len = (self.width ** 2 + 1) - ((self.width // 2 + 1) ** 2)

        # --- Build the stack of movable tiles ---
        # 9 corner tiles without treasures
        stack = [Tile(TileType.CORNER, TileOrientation(randint(0, 3))) for _ in range(int((stack_len-12) * 0.33))]

        # 6 corner tiles with treasures (treasure IDs 22–27)
        stack += [Tile(TileType.CORNER, TileOrientation(randint(0, 3)), TreasureType(i+22)) for i in range(6)]

        # 6 T‑pieces with treasures (treasure IDs 16–21)
        stack += [Tile(TileType.T_PIECE, TileOrientation(randint(0, 3)), TreasureType(i+16)) for i in range(6)]

        # 13 straight tiles without treasures (only 0° or 180° matter)
        stack += [Tile(TileType.STRAIGHT, TileOrientation(randint(0, 1))) for _ in range(int((stack_len-12) * 0.66))]

        # fill rounding Error with corners
        if len(stack) < self.width ** 2 + 1:
            stack += [Tile(TileType.CORNER, TileOrientation(randint(0, 3))) for _ in range(stack_len-len(stack))]
        # delete rounding Error
        stack = stack[:stack_len]

        shuffle(stack)
        self.stack = stack

    # -------------------------------------------------------------------------
    # Tile adjacency + movement logic
    # -------------------------------------------------------------------------

    def get_neighbour(self, position: Tuple[int, int], direction: TileOrientation) -> tuple[int, int] | None:
        """
        Returns the neighbouring coordinate in the given direction.
        Returns None if the neighbour would be outside the board.
        """

        x, y = position

        # Check board boundaries
        if y == 0 and direction == TileOrientation.NORTH:
            return None
        if y == self.width - 1 and direction == TileOrientation.SOUTH:
            return None
        if x == 0 and direction == TileOrientation.WEST:
            return None
        if x == self.width - 1 and direction == TileOrientation.EAST:
            return None

        # Return neighbour coordinate
        if direction == TileOrientation.NORTH:
            return x, y - 1
        if direction == TileOrientation.EAST:
            return x + 1, y
        if direction == TileOrientation.SOUTH:
            return x, y + 1
        if direction == TileOrientation.WEST:
            return x - 1, y

    def move_possible(self, position: Tuple[int, int], direction: TileOrientation) -> bool:
        """
        Checks whether movement from a tile in a given direction is allowed.

        Conditions:
        - current tile must have an open path in that direction
        - neighbour must exist
        - neighbour must have an open path back toward this tile
        """

        # Current tile has no opening in that direction
        if self.tiles[position].path[direction.value] == 0:
            return False

        neighbour = self.get_neighbour(position, direction)
        if neighbour is None:
            return False

        # Neighbour must have opening in opposite direction
        if self.tiles[neighbour].path[(direction.value + 2) % 4] == 0:
            return False

        return True

    # -------------------------------------------------------------------------
    # Pathfinding
    # -------------------------------------------------------------------------

    def pathvalidating(self, start_position: Tuple[int, int], end_position: Tuple[int, int]) -> bool:
        """Returns True if end_position is reachable from start_position."""
        return end_position in self.pathfind(start_position)

    def pathfind(self, position: Tuple[int, int], visited : list[Tuple[int, int]] = []) -> list[Tuple[int, int]]:
        """
        Depth‑first search to find all reachable tiles from a starting position.
        """

        visited.append(position)

        # Explore all 4 directions
        for d in range(4):
            direction = TileOrientation(d)
            neighbour = self.get_neighbour(position, direction)

            # can I move to this neighbour?
            if neighbour and neighbour not in visited:
                if self.move_possible(position, direction):
                    self.pathfind(neighbour, visited)

        # return all visited (which means all reachable) tiles
        return visited

    # -------------------------------------------------------------------------
    # Board construction
    # -------------------------------------------------------------------------

    def create_board(self):
        """
        Creates the fixed tiles (corners + T‑pieces on even coordinates)
        and leaves the remaining spaces as None to be filled later.
        """

        # fill stack with blanks to get a random distribution of treasure or no treasure over all fixed tiles
        treasure_stack = [None for _ in range(((self.width // 2) + 1)**2 - 4)] # gaps² - 4 corners
        # add 12 treasure to the treasure stack
        treasure_stack[:12] = [TreasureType(i+4) for i in range(12)]
        shuffle(treasure_stack)
        counter = 0

        for i in range(self.width):
            for j in range(self.width):

                # --- Fixed corner tiles ---
                if i == 0 and j == 0:
                    self.tiles[(j, i)] = Tile(TileType.CORNER, TileOrientation.EAST, TreasureType.YELLOW)
                elif i == 0 and j == self.width - 1:
                    self.tiles[(j, i)] = Tile(TileType.CORNER, TileOrientation.SOUTH, TreasureType.BLUE)
                elif i == self.width - 1 and j == 0:
                    self.tiles[(j, i)] = Tile(TileType.CORNER, TileOrientation.NORTH, TreasureType.RED)
                elif i == self.width - 1 and j == self.width - 1:
                    self.tiles[(j, i)] = Tile(TileType.CORNER, TileOrientation.WEST, TreasureType.GREEN)

                # --- Fixed T‑pieces on edges (even coordinates only) ---
                elif i == 0 and j % 2 == 0 and 0 < j < self.width - 1:
                    self.tiles[(j, i)] = Tile(TileType.T_PIECE, TileOrientation.EAST, treasure_stack[counter])
                    counter += 1
                elif i == self.width - 1 and j % 2 == 0 and 0 < j < self.width - 1:
                    self.tiles[(j, i)] = Tile(TileType.T_PIECE, TileOrientation.NORTH, treasure_stack[counter])
                    counter += 1
                elif j == 0 and i % 2 == 0 and 0 < i < self.width - 1:
                    self.tiles[(j, i)] = Tile(TileType.T_PIECE, TileOrientation.EAST, treasure_stack[counter])
                    counter += 1
                elif j == self.width - 1 and i % 2 == 0 and 0 < i < self.width - 1:
                    self.tiles[(j, i)] = Tile(TileType.T_PIECE, TileOrientation.WEST, treasure_stack[counter])
                    counter += 1

                # --- Middle T‑pieces (even/even coordinates) ---
                elif i % 2 == 0 and j % 2 == 0:
                    self.tiles[(j, i)] = Tile(TileType.T_PIECE, TileOrientation(randint(0, 3)), treasure_stack[counter])
                    counter += 1

                # --- Remaining spaces are filled later ---
                else:
                    self.tiles[(j, i)] = None

    def create_blocked_board(self):
        """Creates a board filled entirely with WALL tiles (for debugging)."""
        for i in range(self.width):
            for j in range(self.width):
                self.tiles[(j, i)] = Tile(TileType.WALL, TileOrientation.NORTH)

    def change_tile(self, x: int, y: int, tile):
        """Replaces the tile at (x, y) with a new tile."""
        self.tiles[(x, y)] = tile

    def fill_board(self):
        """
        Fills all None‑spaces with tiles from the stack.
        The last remaining tile becomes the spare tile.
        """

        counter = 0
        for i in range(self.width):
            for j in range(self.width):
                if self.tiles[(j, i)] is None:
                    self.tiles[(j, i)] = self.stack[counter]
                    counter += 1

        # spare tile for insertion later
        self.spare = self.stack[counter]

    # -------------------------------------------------------------------------
    # Tile insertion (Labyrinth mechanics)
    # -------------------------------------------------------------------------

    def insert_tile(self, x, y):
        """
        Inserts the spare tile into the board at (x, y), shifting a full row/column.

        Rules:
        - Only border positions allowed
        - Only odd coordinates are movable (even ones are fixed)
        - Tile must be inserted from outside the board
        """

        # Must be on the border
        if (x != 0 and y != 0) and (x != self.width - 1 and y != self.width - 1):
            raise BoardError("You can't insert a tile in the middle")

        # Must be inside valid coordinate range
        if x < 0 or x >= self.width or y < 0 or y >= self.width:
            raise BoardError("You can't insert a tile outside the board")

        # Even/even positions are fixed tiles
        if x % 2 == 0 and y % 2 == 0:
            raise BoardError("That tile isn't movable")

        # --- Horizontal insertion from the left ---
        if x == 0:
            for i in range(self.width):
                ram = self.tiles[(i, y)]
                self.tiles[(i, y)] = self.spare
                self.spare = ram

        # --- Horizontal insertion from the right ---
        if x == self.width - 1:
            for i in range(self.width - 1, -1, -1):
                ram = self.tiles[(i, y)]
                self.tiles[(i, y)] = self.spare
                self.spare = ram

        # --- Vertical insertion from the top ---
        if y == 0:
            for i in range(self.width):
                ram = self.tiles[(x, i)]
                self.tiles[(x, i)] = self.spare
                self.spare = ram

        # --- Vertical insertion from the bottom ---
        if y == self.width - 1:
            for i in range(self.width - 1, -1, -1):
                ram = self.tiles[(x, i)]
                self.tiles[(x, i)] = self.spare
                self.spare = ram
