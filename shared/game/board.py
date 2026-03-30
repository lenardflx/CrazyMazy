# Author: Lennart William Owen, Raphael Eiden, Sarah Trapp, Lenard Felix

from __future__ import annotations

from random import randint, shuffle
from uuid import UUID

from shared.types.data import GameData, TileData
from shared.types.enums import InsertionSide, TileOrientation, TileType, TreasureType
from shared.types.payloads import TilePayload
from shared.state.errors import BoardError
from shared.game.tile import Tile

Position = tuple[int, int]


def movable_insertion_indexes(board_size: int) -> tuple[int, ...]:
    return tuple(range(1, board_size, 2))


def is_valid_insertion_index(board_size: int, index: int) -> bool:
    return index in movable_insertion_indexes(board_size)


def opposite_side(side: InsertionSide) -> InsertionSide:
    return {
        InsertionSide.TOP: InsertionSide.BOTTOM,
        InsertionSide.RIGHT: InsertionSide.LEFT,
        InsertionSide.BOTTOM: InsertionSide.TOP,
        InsertionSide.LEFT: InsertionSide.RIGHT,
    }[side]

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
        self._tile_entities: dict[int, TileData] = {}

        # make a treasure list for better distribution across movable and non-movable tiles
        self.treasure_list = list(TreasureType)

    @classmethod
    def create_runtime(cls, game: GameData) -> "Board":
        board = cls(game.board_size)
        board.create_board()
        board.fill_board()
        board._initialize_tile_entities(game.id)
        return board

    @classmethod
    def from_tile_data(cls, game: GameData, tiles: list[TileData]) -> "Board":
        board = cls(game.board_size)
        board.stack = []
        for entity in tiles:
            tile = Tile.from_tile_data(entity)
            board._tile_entities[id(tile)] = entity
            if entity.is_spare:
                if board.spare is not None:
                    raise ValueError("Game data contains multiple spare tiles")
                board.spare = tile
                continue
            if entity.row is None or entity.column is None:
                raise ValueError("Board tile is missing row or column")
            board.tiles[(entity.column, entity.row)] = tile
        if board.spare is None:
            raise ValueError("Game data contains no spare tile")
        return board

    @classmethod
    def from_payloads(cls, width: int, tiles: list[TilePayload]) -> "Board":
        board = cls(width)
        board.stack = []
        for payload in tiles:
            tile = Tile.from_payload(payload)
            if payload["is_spare"]:
                if board.spare is not None:
                    raise ValueError("Board payload contains multiple spare tiles")
                board.spare = tile
                continue
            if "column" not in payload or "row" not in payload:
                raise ValueError("Board payload tile is missing row/column")
            board.tiles[(payload["column"], payload["row"])] = tile
        if board.spare is None:
            raise ValueError("Board payload contains no spare tile")
        return board

    def to_tile_data(self, game_id: UUID) -> list[TileData]:
        result: list[TileData] = []
        for y in range(self.width):
            for x in range(self.width):
                tile = self.tiles[(x, y)]
                if tile is None:
                    continue
                entity = self._require_tile_entity(tile, game_id)
                entity.game_id = game_id
                entity.row = y
                entity.column = x
                entity.rotation = tile.orientation.value
                entity.tile_type = tile.type
                entity.treasure_type = tile.treasure
                entity.is_spare = False
                result.append(entity)

        if self.spare is None:
            raise ValueError("Board has no spare tile")
        spare_entity = self._require_tile_entity(self.spare, game_id)
        spare_entity.game_id = game_id
        spare_entity.row = None
        spare_entity.column = None
        spare_entity.rotation = self.spare.orientation.value
        spare_entity.tile_type = self.spare.type
        spare_entity.treasure_type = self.spare.treasure
        spare_entity.is_spare = True
        result.append(spare_entity)
        return result

    # -------------------------------------------------------------------------
    # Tile adjacency + movement logic
    # -------------------------------------------------------------------------

    def get_neighbour(self, position: Position, direction: TileOrientation) -> Position | None:
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

    def move_possible(self, position: Position, direction: TileOrientation) -> bool:
        """
        Checks whether movement from a tile in a given direction is allowed.

        Conditions:
        - current tile must have an open path in that direction
        - neighbour must exist
        - neighbour must have an open path back toward this tile
        """

        # Current tile has no opening in that direction
        current = self.tiles[position]
        if current is None or current.path[direction.value] == 0:
            return False

        neighbour = self.get_neighbour(position, direction)
        if neighbour is None:
            return False

        # Neighbour must have opening in opposite direction
        other = self.tiles.get(neighbour)
        if other is None or other.path[(direction.value + 2) % 4] == 0:
            return False

        return True

    # -------------------------------------------------------------------------
    # Pathfinding
    # -------------------------------------------------------------------------

    def reachable_positions(self, start: Position) -> set[Position]:
        return set(self.pathfind(start))

    def can_reach(self, start: Position, destination: Position) -> bool:
        return destination in self.reachable_positions(start)

    def path_to(self, start: Position, destination: Position) -> list[Position] | None:
        if not self.can_reach(start, destination):
            return None
        # TODO: Replace this placeholder with the real path reconstruction algorithm.
        return [start, destination]

    def pathfind(self, position: Position, visited: list[Position] | None = None) -> list[Position]:
        """
        Depth‑first search to find all reachable tiles from a starting position.
        """
        if visited is None:
            visited = []

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
        treasure_stack: list[TreasureType | None] = [None for _ in range(((self.width // 2) + 1)**2 - 4)] # gaps² - 4 corners
        # add 12 treasure to the treasure stack
        treasure_stack[:12] = [TreasureType(self.treasure_list[i]) for i in range(12)]
        shuffle(treasure_stack)
        counter = 0

        for i in range(self.width):
            for j in range(self.width):

                # --- Fixed corner tiles ---
                if i == 0 and j == 0:
                    self.tiles[(j, i)] = Tile(TileType.CORNER, TileOrientation.EAST)
                elif i == 0 and j == self.width - 1:
                    self.tiles[(j, i)] = Tile(TileType.CORNER, TileOrientation.SOUTH)
                elif i == self.width - 1 and j == 0:
                    self.tiles[(j, i)] = Tile(TileType.CORNER, TileOrientation.NORTH)
                elif i == self.width - 1 and j == self.width - 1:
                    self.tiles[(j, i)] = Tile(TileType.CORNER, TileOrientation.WEST)

                # --- Fixed T‑pieces on edges (even coordinates only) ---
                elif i == 0 and j % 2 == 0 and 0 < j < self.width - 1:
                    self.tiles[(j, i)] = Tile(TileType.T, TileOrientation.SOUTH, treasure_stack[counter])
                    counter += 1
                elif i == self.width - 1 and j % 2 == 0 and 0 < j < self.width - 1:
                    self.tiles[(j, i)] = Tile(TileType.T, TileOrientation.NORTH, treasure_stack[counter])
                    counter += 1
                elif j == 0 and i % 2 == 0 and 0 < i < self.width - 1:
                    self.tiles[(j, i)] = Tile(TileType.T, TileOrientation.EAST, treasure_stack[counter])
                    counter += 1
                elif j == self.width - 1 and i % 2 == 0 and 0 < i < self.width - 1:
                    self.tiles[(j, i)] = Tile(TileType.T, TileOrientation.WEST, treasure_stack[counter])
                    counter += 1

                # --- Middle T‑pieces (even/even coordinates) ---
                elif i % 2 == 0 and j % 2 == 0:
                    self.tiles[(j, i)] = Tile(TileType.T, TileOrientation(randint(0, 3)), treasure_stack[counter])
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

        # lenght of stack
        stack_len = (self.width ** 2 + 1) - ((self.width // 2 + 1) ** 2) # boardsize² - fixed tiles

        # --- Build the stack of movable tiles ---
        # 9 corner tiles without treasures
        stack = [Tile(TileType.CORNER, randint(0, 3)) for _ in range(int((stack_len-12) * 0.33))]

        # 6 corner tiles with treasures (treasure IDs 22–27)
        stack += [Tile(TileType.CORNER, randint(0, 3), self.treasure_list[i+18]) for i in range(6)] # not a clean solution for the treasures but it works

        # 6 T‑pieces with treasures (treasure IDs 16–21)
        stack += [Tile(TileType.T, randint(0, 3), self.treasure_list[i+12]) for i in range(6)]

        # 13 straight tiles without treasures (only 0° or 180° matter)
        stack += [Tile(TileType.STRAIGHT, randint(0, 1)) for _ in range(int((stack_len-12) * 0.66))]

        # fill rounding Error with corners
        if len(stack) < self.width ** 2 + 1:
            stack += [Tile(TileType.CORNER, randint(0, 3)) for _ in range(stack_len-len(stack))]
        # delete rounding Error
        stack = stack[:stack_len]

        shuffle(stack)

        counter = 0
        for i in range(self.width):
            for j in range(self.width):
                if self.tiles[(j, i)] is None:
                    self.tiles[(j, i)] = stack[counter]
                    counter += 1

        # spare tile for insertion later
        self.spare = stack[counter]

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

        if self.spare is None:
            raise BoardError("Board has no spare tile")

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

    def shift_tile(self, side: InsertionSide, index: int, rotation: int) -> None:
        if not is_valid_insertion_index(self.width, index):
            raise ValueError(f"Invalid insertion index: {index}")
        if self.spare is None:
            raise ValueError("Board has no spare tile")
        self.spare.orientation = TileOrientation((self.spare.orientation.value + rotation) % 4)
        self.spare.set_paths()
        x, y = self._insertion_coordinates(side, index)
        self.insert_tile(x, y)

    def shift_player_position(self, position: Position | None, side: InsertionSide, index: int) -> Position | None:
        if position is None:
            return None
        x, y = position
        if side in (InsertionSide.LEFT, InsertionSide.RIGHT) and y != index:
            return position
        if side in (InsertionSide.TOP, InsertionSide.BOTTOM) and x != index:
            return position
        if side == InsertionSide.LEFT:
            return ((x + 1) % self.width, y)
        if side == InsertionSide.RIGHT:
            return ((x - 1) % self.width, y)
        if side == InsertionSide.TOP:
            return (x, (y + 1) % self.width)
        return (x, (y - 1) % self.width)

    def tile_treasure_at(self, position: Position) -> TreasureType | None:
        tile = self.tiles[position]
        if tile is None:
            return None
        return tile.treasure

    def _insertion_coordinates(self, side: InsertionSide, index: int) -> Position:
        if side == InsertionSide.LEFT:
            return 0, index
        if side == InsertionSide.RIGHT:
            return self.width - 1, index
        if side == InsertionSide.TOP:
            return index, 0
        return index, self.width - 1

    def _initialize_tile_entities(self, game_id: UUID) -> None:
        self._tile_entities = {}
        for tile in self.tiles.values():
            if tile is not None:
                self._tile_entities[id(tile)] = TileData(game_id=game_id)
        if self.spare is not None:
            self._tile_entities[id(self.spare)] = TileData(game_id=game_id)

    def _require_tile_entity(self, tile: Tile, game_id: UUID) -> TileData:
        entity = self._tile_entities.get(id(tile))
        if entity is None:
            entity = TileData(game_id=game_id)
            self._tile_entities[id(tile)] = entity
        return entity

    def is_border(self, position: tuple[int, int]) -> bool:
        # returns if a position is at the border of the board
        return 0 in position or self.width in position

    def insertion_shift_coordinates(self, position : tuple[int, int]) -> list[tuple[int,int]]:
        '''
        returns a list with the coordinates of all tiles that move after an insertion
        '''

        x,y = position
        moved_tiles = []

        # --- Horizontal insertion from the left ---
        if x == 0:
            for i in range(self.width):
                moved_tiles += [(i,y)]

        # --- Horizontal insertion from the right ---
        if x == self.width - 1:
            for i in range(self.width - 1, -1, -1):
                moved_tiles += [(i, y)]

        # --- Vertical insertion from the top ---
        if y == 0:
            for i in range(self.width):
                moved_tiles += [(x, i)]

        # --- Vertical insertion from the bottom ---
        if y == self.width - 1:
            for i in range(self.width - 1, -1, -1):
                moved_tiles += [(x, i)]