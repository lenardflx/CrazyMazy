# Author: Lennart William Owen, Raphael Eiden, Sarah Trapp, Lenard Felix

from collections import deque
from enum import Enum
from random import randint, shuffle
from dataclasses import dataclass
from uuid import UUID

from shared.models import (
    GameData,
    GamePhase,
    InsertionSide,
    PlayerColor,
    PlayerData,
    PlayerResult,
    PlayerStatus,
    TileData,
    TileOrientation,
    TileType,
    TreasureData,
    TreasureType,
    TurnPhase,
)
from shared.schema import GameSnapshotPayload, PublicPlayerPayload, TilePayload, ViewerPayload
from shared.state.errors import BoardError

Position = tuple[int, int]

def start_position_for_color(board_size: int, color: PlayerColor) -> Position:
    return {
        PlayerColor.RED: (0, 0),
        PlayerColor.BLUE: (board_size - 1, 0),
        PlayerColor.GREEN: (0, board_size - 1),
        PlayerColor.YELLOW: (board_size - 1, board_size - 1),
    }[color]


def home_color_for_position(board_size: int, position: Position) -> PlayerColor | None:
    for color in PlayerColor:
        if start_position_for_color(board_size, color) == position:
            return color
    return None


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


def assign_treasures(player_count: int) -> list[list[TreasureType]]:
    treasure_types = list(TreasureType)
    shuffle(treasure_types)
    return [treasure_types[offset * 6:(offset + 1) * 6] for offset in range(player_count)]


class Tile:
    def __init__(self, type: TileType, orientation: TileOrientation | int, treasure: None | TreasureType = None):
        """
        Represents a single tile on the board.

        Args:
            type: The structural tile type (STRAIGHT, CORNER, T_PIECE, WALL(just for testing)).
            orientation: The current rotation of the tile (NORTH/EAST/SOUTH/WEST).
            treasure: Optional treasure placed on this tile.
        """

        # Basic tile metadata
        self.type = TileType(type)
        self.orientation = TileOrientation(orientation)
        self.treasure = None if treasure is None else TreasureType(treasure)
        
        # Path connectivity in order [N, E, S, W]
        # Example: [1,0,1,0] means open to North + South
        self.path = None

        # Compute initial path layout based on type + orientation
        self.set_paths()

    def set_paths(self) -> None:
        """
        Computes the tile's connectivity (open paths) based on its type and orientation.

        Base patterns are defined for NORTH orientation.
        Then we rotate the deque to match the actual orientation.
        """

        # base path pattern for orientation NORTH
        parse_Tiletype = {TileType.STRAIGHT: [1,0,1,0], # N E S W
                          TileType.CORNER : [1,1,0,0],
                          TileType.T : [1,1,0,1],
                          TileType.WALL : [0,0,0,0]}
        # set exit values for path
        path = deque(parse_Tiletype[self.type])


        # Rotate the connectivity pattern according to orientation
        # TileOrientation.value is 0=N, 1=E, 2=S, 3=W
        path.rotate(TileOrientation(self.orientation).value)

        # Convert deque → list for easier use elsewhere
        self.path = list(path)

    def rotate_left(self):
        """
        Rotates the tile 90° counter-clockwise.

        Updates:
        - orientation
        - path connectivity
        """

        # Decrease orientation index modulo 4
        self.orientation = TileOrientation((self.orientation.value - 1) % 4)

        # Recompute connectivity
        self.set_paths()

    def rotate_right(self):
        """
        Rotates the tile 90° clockwise.

        Updates:
        - orientation
        - path connectivity
        """

        # Increase orientation index modulo 4
        self.orientation = TileOrientation((self.orientation.value + 1) % 4)

        # Recompute connectivity
        self.set_paths()

    @classmethod
    def from_payload(cls, payload: TilePayload) -> "Tile":
        return cls(
            payload["tile_type"],
            payload["rotation"],
            payload["treasure_type"],
        )

    @classmethod
    def from_tile_data(cls, tile: TileData) -> "Tile":
        return cls(tile.tile_type, tile.rotation, tile.treasure_type)


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
                    self.tiles[(j, i)] = Tile(TileType.T, TileOrientation.EAST, treasure_stack[counter])
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
        self.spare.orientation = TileOrientation(rotation % 4)
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


@dataclass(slots=True)
class GameState:
    """Runtime aggregate built from persisted game, player, tile and treasure data."""

    game: GameData
    players: list[PlayerData]
    board: Board | None
    treasures_by_player: dict[UUID, list[TreasureData]]

    @property
    def tiles(self) -> list[TileData]:
        if self.board is None:
            return []
        return self.board.to_tile_data(self.game.id)

    @classmethod
    def from_models(
        cls,
        game: GameData,
        players: list[PlayerData],
        tiles: list[TileData],
        treasures_by_player: dict[UUID, list[TreasureData]],
    ) -> "GameState":
        return cls(
            game=game,
            players=players,
            board=Board.from_tile_data(game, tiles) if tiles else None,
            treasures_by_player=treasures_by_player,
        )


@dataclass(slots=True)
class SnapshotPlayerState:
    id: str
    display_name: str
    join_order: int
    piece_color: PlayerColor
    position: Position | None
    status: PlayerStatus
    result: PlayerResult
    placement: int | None
    collected_treasures: list[TreasureType]
    remaining_treasure_count: int

    @classmethod
    def from_payload(cls, payload: PublicPlayerPayload) -> "SnapshotPlayerState":
        position_payload = payload["position"]
        position = None if position_payload is None else (position_payload["x"], position_payload["y"])
        return cls(
            id=payload["id"],
            display_name=payload["display_name"],
            join_order=payload["join_order"],
            piece_color=PlayerColor(payload["piece_color"]),
            position=position,
            status=PlayerStatus(payload["status"]),
            result=PlayerResult(payload["result"]),
            placement=payload["placement"],
            collected_treasures=[TreasureType(treasure) for treasure in payload["collected_treasures"]],
            remaining_treasure_count=payload["remaining_treasure_count"],
        )

    @property
    def collected_treasure_count(self) -> int:
        return len(self.collected_treasures)

    @property
    def is_departed(self) -> bool:
        return self.status == PlayerStatus.DEPARTED

    @property
    def is_observer(self) -> bool:
        return self.status == PlayerStatus.OBSERVER

    @property
    def is_inactive(self) -> bool:
        return self.is_departed or self.is_observer

    # TODO: better layout, and this sucks :(
    def sidebar_status(self, *, post_game: bool = False) -> str | None:
        if self.is_departed:
            return "Left"
        if self.is_observer:
            return "Spectator"
        if post_game and self.placement is not None:
            return "Finished"
        return None


@dataclass(slots=True)
class SnapshotViewerState:
    player_id: str
    is_leader: bool
    is_current_player: bool
    active_treasure_type: TreasureType | None
    collected_treasures: list[TreasureType]
    remaining_treasure_count: int

    @classmethod
    def from_payload(cls, payload: ViewerPayload) -> "SnapshotViewerState":
        active_treasure_type = payload["active_treasure_type"]
        return cls(
            player_id=payload["player_id"],
            is_leader=payload["is_leader"],
            is_current_player=payload["is_current_player"],
            active_treasure_type=None if active_treasure_type is None else TreasureType(active_treasure_type),
            collected_treasures=[TreasureType(treasure) for treasure in payload["collected_treasures"]],
            remaining_treasure_count=payload["remaining_treasure_count"],
        )


@dataclass(slots=True)
class SnapshotTurnState:
    current_player_id: str | None
    phase: TurnPhase | None


@dataclass(slots=True)
class SnapshotGameState:
    game_id: str
    code: str
    phase: GamePhase
    revision: int
    board_size: int
    leader_player_id: str | None
    turn: SnapshotTurnState
    board: Board | None
    players: list[SnapshotPlayerState]
    reachable_positions: set[Position]
    viewer: SnapshotViewerState | None = None

    @property
    def ordered_players(self) -> list[SnapshotPlayerState]:
        return sorted(self.players, key=lambda player: player.join_order)

    @property
    def viewer_id(self) -> str:
        return "" if self.viewer is None else self.viewer.player_id

    @property
    def viewer_player(self) -> SnapshotPlayerState | None:
        return next((player for player in self.players if player.id == self.viewer_id), None)

    @property
    def current_player_id(self) -> str:
        return "" if self.turn.current_player_id is None else self.turn.current_player_id

    @property
    def active_treasure_type(self) -> TreasureType | None:
        return None if self.viewer is None else self.viewer.active_treasure_type

    @property
    def viewer_turn(self) -> bool:
        return self.viewer_id == self.current_player_id

    @property
    def viewer_is_spectator(self) -> bool:
        viewer = self.viewer_player
        return viewer is not None and viewer.is_observer

    @property
    def can_shift(self) -> bool:
        return self.viewer_turn and self.turn.phase == TurnPhase.SHIFT

    @property
    def can_move(self) -> bool:
        return self.viewer_turn and self.turn.phase == TurnPhase.MOVE

    @property
    def turn_prompt(self) -> str:
        if self.viewer_is_spectator:
            return "Spectating"
        if self.can_shift:
            return "Your turn: insert a tile"
        if self.can_move:
            return "Your turn: move"
        return "Waiting for another player"

    @property
    def spare_tile(self) -> Tile | None:
        if self.board is None:
            return None
        return self.board.spare

    def rotated_spare_tile(self, rotation: int) -> Tile | None:
        tile = self.spare_tile
        if tile is None:
            return None
        return type(tile)(tile.type, (tile.orientation.value + rotation) % 4, tile.treasure)

    def tile_at(self, position: Position) -> Tile | None:
        if self.board is None:
            return None
        return self.board.tiles.get(position)

    def is_position_reachable(self, position: Position) -> bool:
        return position in self.reachable_positions

    def home_color_at(self, position: Position) -> PlayerColor | None:
        return home_color_for_position(self.board_size, position)

    @classmethod
    def from_snapshot(cls, snapshot: GameSnapshotPayload) -> "SnapshotGameState":
        turn_phase = snapshot["turn"]["turn_phase"]
        phase = GamePhase(snapshot["phase"])
        return cls(
            game_id=snapshot["game_id"],
            code=snapshot["code"],
            phase=phase,
            revision=snapshot["revision"],
            board_size=snapshot["board_size"],
            leader_player_id=snapshot["leader_player_id"],
            turn=SnapshotTurnState(
                current_player_id=snapshot["turn"]["current_player_id"],
                phase=None if turn_phase is None else TurnPhase(turn_phase),
            ),
            board=_board_from_snapshot(snapshot["board_size"], snapshot["tiles"], phase),
            players=[SnapshotPlayerState.from_payload(player) for player in snapshot["players"]],
            reachable_positions={(position["x"], position["y"]) for position in snapshot["reachable_positions"]},
            viewer=None if snapshot["viewer"] is None else SnapshotViewerState.from_payload(snapshot["viewer"]),
        )


def _board_from_snapshot(board_size: int, tiles: list[TilePayload], phase: GamePhase) -> Board | None:
    if not tiles:
        if phase == GamePhase.GAME:
            raise ValueError("Active game snapshot is missing board tiles")
        return None
    return Board.from_payloads(board_size, tiles)
