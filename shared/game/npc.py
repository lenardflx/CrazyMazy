from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from uuid import UUID

from shared.game.board import Board, Position
from shared.types.enums import InsertionSide, NpcDifficulty


@dataclass(slots=True, frozen=True)
class NpcTurn:
    shift_side: InsertionSide
    shift_index: int
    shift_rotation: int
    move_to: Position | None = None


@dataclass(slots=True)
class Npc:
    """Represents a non-player character in the game, with logic to choose turns."""

    player_id: UUID
    difficulty: NpcDifficulty = NpcDifficulty.NORMAL

    def expand_reachable(self, reachable_tiles : set[Position]) -> list[Position]:
        """
        expands a path with all adjacent tiles

        used in choose_turn method to check if an insertion has an effect on reachable paths
        """
        # can currently add coordinates outside the board TODO: remove those coordinates
        new_tiles = []
        for coordinate in reachable_tiles:
            new_tiles += [(coordinate[0]+1, coordinate[1]),
                          (coordinate[0], coordinate[1]+1),
                          (coordinate[0]-1, coordinate[1]),
                          (coordinate[0], coordinate[1]-1)]
        return list(reachable_tiles) + new_tiles

    def get_distance(self, start : Position, finish : Position) -> int:
        """returns the distance from start to finish"""
        return abs(finish[0]-start[0]) + abs(finish[1]-start[1])

    def _get_expanded_reachable(self, board: Board, current_position: Position) -> list[Position]:
        # generate currently reachable tiles
        reachable_tiles = board.reachable_positions(current_position)

        # expand reachable tiles
        return self.expand_reachable(reachable_tiles)

    def _collect_insertion_tiles(self, board: Board, expanded_reachable: list[Position]) -> list[Position]:
        # check for which insertion a path has to be computed
        insertion_tiles = [] # coordinates of every tile where an insertion has an effect

        """
        get the coordinates of every insertion that makes a difference to the reachable tiles
        
        no need to compute new paths if the insertion doesn't affect the outcome
        """
        # top row
        for i in range(1,board.width-1):
            if any(coordinate in board.insertion_shift_coordinates((i,0)) for coordinate in expanded_reachable):
                insertion_tiles += [(i,0)]

        # bottom row
        for i in range(1,board.width-1):
            if any(coordinate in board.insertion_shift_coordinates((i,board.width - 1)) for coordinate in expanded_reachable):
                insertion_tiles += [(i,board.width - 1)]

        # left row
        for i in range(1, board.width-1):
            if any(coordinate in board.insertion_shift_coordinates((0,i)) for coordinate in
                   expanded_reachable):
                insertion_tiles += [(0, i)]

        # right row
        for i in range(1,board.width-1):
            if any(coordinate in board.insertion_shift_coordinates((board.width - 1, i)) for coordinate in expanded_reachable):
                insertion_tiles += [(board.width - 1, i)]

        return insertion_tiles

    def _remove_blocked_insertion(
        self,
        board: Board,
        insertion_tiles: list[Position],
        blocked_side: InsertionSide | None,
        blocked_index: int | None,
    ) -> None:
        # remove blocked insertion
        if blocked_side is None or blocked_index is None:
            return
        blocked_tile = board.insertion_coordinates(blocked_side, blocked_index)
        insertion_tiles[:] = [tile for tile in insertion_tiles if tile != blocked_tile]

    def _evaluate_insertion(
        self,
        board: Board,
        insertion: Position,
        current_position: Position,
        target_position: Position | None,
        target_on_spare: bool,
        best_so_far: Position | None,
        best_value: int,
        best_insertion: Position | None,
    ) -> tuple[Position | None, int, Position | None, bool]:
        # get treasure coordinates after insertion
        if target_on_spare:
            current_treasure_coordinates = insertion
        else:
            if target_position is None:
                raise ValueError("NPC target is missing from both board and spare tile")
            current_treasure_coordinates = board.position_after_insert(target_position, insertion)
        insertion_side, insertion_index = board.convert_insertion(insertion[0], insertion[1])
        current_position_after_insert = board.shift_player_position(
            current_position,
            insertion_side,
            insertion_index,
        )
        if current_position_after_insert is None:
            raise ValueError("NPC current position became invalid after insertion")

        # check if treasure is the spare
        if current_treasure_coordinates is not None:
            board_copy : Board = deepcopy(board) # copy board to make non-permanent insertions

            # make an insertion
            board_copy.insert_tile(insertion[0], insertion[1])

            # compute all tiles that are reachable after the insertion
            reachable_tiles = board_copy.reachable_positions(current_position_after_insert)

            # check if insertion lead to a direct path to the treasure
            if current_treasure_coordinates in reachable_tiles:
                best_insertion = insertion
                best_so_far = current_treasure_coordinates
                return best_so_far, best_value, best_insertion, True

            # get the closest to the treasure
            else:
                # check distance to the treasure of every reachable tile and change best_so_far if there is a closer tile
                for position in reachable_tiles:
                    distance = self.get_distance(position, current_treasure_coordinates)
                    if distance < best_value:
                        best_so_far = position
                        best_value = distance
                        best_insertion = insertion

        return best_so_far, best_value, best_insertion, False

    def _find_best_move(
        self,
        board: Board,
        insertion_tiles: list[Position],
        current_position: Position,
        target_position: Position | None,
        target_on_spare: bool,
    ) -> tuple[Position | None, Position | None]:
        best_so_far = None # best coordinates so far
        best_value = board.width**2 # best distance to the target so far
        best_insertion = None # insertion that was done to get the best_value

        # Evaluate every relevant insertion independently on a fresh board copy.
        for insertion in insertion_tiles:
            best_so_far, best_value, best_insertion, found_direct_path = self._evaluate_insertion(
                board,
                insertion,
                current_position,
                target_position,
                target_on_spare,
                best_so_far,
                best_value,
                best_insertion,
            )
            if found_direct_path:
                break # no need to finish the algorithm

        return best_so_far, best_insertion

    def _build_turn(
        self,
        board: Board,
        best_insertion: Position,
        best_so_far: Position | None,
    ) -> NpcTurn:
        return NpcTurn(
            shift_side=board.convert_insertion(best_insertion[0], best_insertion[1])[0],
            shift_index=board.convert_insertion(best_insertion[0], best_insertion[1])[1],
            # TODO: Each Rotation
            shift_rotation=0,
            move_to=(best_so_far[0], best_so_far[1]) if best_so_far is not None else None,
        )

    def choose_turn(self, board: Board, current_position: Position | None, target_position : Position | None, blocked_side: InsertionSide | None = None, blocked_index: int | None = None, target_on_spare: bool = False,) -> NpcTurn:
        """Choose a full deterministic turn plan for the current board state."""

        if current_position is None:
            raise ValueError("NPC turn requires a current position")

        expanded_reachable = self._get_expanded_reachable(board, current_position)
        insertion_tiles = self._collect_insertion_tiles(board, expanded_reachable)
        self._remove_blocked_insertion(board, insertion_tiles, blocked_side, blocked_index)
        if not insertion_tiles:
            raise ValueError("NPC could not find a valid insertion")

        if target_position is None and not target_on_spare:
            raise ValueError("NPC target is missing from both board and spare tile")

        # TODO: Use self.difficulty to vary insertion search breadth and move-selection heuristics.
        best_so_far, best_insertion = self._find_best_move(
            board,
            insertion_tiles,
            current_position,
            target_position,
            target_on_spare,
        )
        if best_insertion is None:
            # NOTE: could be resolved but sometimes it was None, so determinic fallback
            best_insertion = insertion_tiles[0]
        return self._build_turn(board, best_insertion, best_so_far)
