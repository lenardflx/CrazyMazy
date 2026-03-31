from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from shared.game.board import Board
from shared.state.errors import BoardError
from shared.types.enums import InsertionSide, NpcDifficulty

if TYPE_CHECKING:
    from shared.game.state import GameState


@dataclass(slots=True, frozen=True)
class NpcTurn:
    shift_side: InsertionSide
    shift_index: int
    shift_rotation: int
    move_to: tuple[int, int] | None = None


@dataclass(slots=True)
class Npc:
    """Represents a non-player character in the game, with logic to choose turns."""

    player_id: UUID
    difficulty: NpcDifficulty = NpcDifficulty.NORMAL

    def expand_reachable(self, board : "Board" ,reachable_tiles : set[tuple[int,int]]) -> list[tuple[int,int]]:
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

    def get_distance(self, start : tuple[int, int], finish : tuple[int,int]) -> int:
        """returns the distance from start to finish"""
        return abs(finish[0]-start[0]) + abs(finish[1]-start[1])

    def choose_turn(self, board: Board, current_position: tuple[int, int], target_position : tuple[int, int], blocked_side: InsertionSide | None = None, blocked_index: int | None = None,) -> NpcTurn:
        """Choose a full deterministic turn plan for the current board state."""

        # check if the board is valid
        if board is None:
            raise ValueError("NPC cannot choose a turn without a board")

        # generate currently reachable tiles
        reachable_tiles = board.reachable_positions(current_position)

        # expand reachable tiles
        expanded_reachable = self.expand_reachable(board, reachable_tiles)

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
                insertion_tiles += [(0, 1)]

        # right row
        for i in range(1,board.width-1):
            if any(coordinate in board.insertion_shift_coordinates((board.width - 1, i)) for coordinate in expanded_reachable):
                insertion_tiles += [(board.width - 1, i)]

        # remove blocked insertion
        blocked_tile = board.insertion_coordinates(blocked_side, blocked_index)
        if blocked_tile in insertion_tiles:
            insertion_tiles.remove(blocked_tile)

        board_copy : Board = deepcopy(board) # copy board to make non-permanent insertions
        layout = board_copy.tiles # copy board layout to test several insertion on the same board
        best_so_far = None # best coordinates so far
        best_value = board.width**2 # best distance to the target so far
        best_insertion = None # insertion that was done to get the best_value

        for insertion in insertion_tiles:
            # get treasure coordinates after insertion
            current_treasure_coordinates = board.position_after_insert(target_position, insertion)
            current_position_after_insert = board.position_after_insert(current_position, insertion)

            # check if treasure is the spare
            if current_treasure_coordinates is not None:

                # make an insertion
                board_copy.insert_tile(insertion[0], insertion[1])

                # compute all tiles that are reachable after the insertion
                reachable_tiles = board_copy.reachable_positions(current_position_after_insert)

                # check if insertion lead to a direct path to the treasure
                if current_treasure_coordinates in reachable_tiles:
                    best_insertion = insertion
                    best_so_far = current_treasure_coordinates
                    break # no need to finish the algorithm

                # get the closest to the treasure
                else:
                    # check distance to the treasure of every reachable tile and change best_so_far if there is a closer tile
                    for position in reachable_tiles:
                        distance = self.get_distance(position, current_treasure_coordinates)
                        if distance < best_value:
                            best_so_far = position
                            best_value = distance
                            best_insertion = insertion

                # undo last insertion
                board_copy.change_board(layout)



        return NpcTurn(
            shift_side=board.convert_insertion(best_insertion[0], best_insertion[1])[0],
            shift_index=board.convert_insertion(best_insertion[0], best_insertion[1])[1],
            shift_rotation=0,
            move_to=(best_so_far[0], best_so_far[1]),
        )
