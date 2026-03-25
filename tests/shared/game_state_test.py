from shared.state.game_state import Board,TileType, Tile, TreasureType, TileOrientation
import unittest

class TestCreateBoard(unittest.TestCase):

    def _randomBoard(self):
        board = Board()
        board.create_board()
        return board

    def test_corners(self):
        # tests if corner have the correct type and colour
        board = self._randomBoard()
        self.assertTrue(board.tiles[(0,0)].type == TileType.CORNER and board.tiles[(0,0)].treasure == TreasureType.YELLOW) # top left
        self.assertTrue(board.tiles[(board.width-1, 0)].type == TileType.CORNER and board.tiles[(board.width-1, 0)].treasure == TreasureType.BLUE) #top right
        self.assertTrue(board.tiles[(0, board.width-1)].type == TileType.CORNER and board.tiles[(0, board.width-1)].treasure == TreasureType.RED) # bottom left
        self.assertTrue(board.tiles[(board.width-1, board.width-1)].type == TileType.CORNER and board.tiles[(board.width-1, board.width-1)].treasure == TreasureType.GREEN) # bottom right


    def test_fixed_tiles_number(self):
        # tests if all fixed tiles are placed on the board
        board = self._randomBoard()
        counter = 0
        for key in board.tiles:
            if board.tiles[key] is not None:
                counter += 1
        self.assertEqual(counter, 16)

    def test_board_full(self):
        # tests if the board is full of tiles
        board = self._randomBoard()
        board.fill_board()
        for i in range(board.width):
            for j in range(board.width):
                self.assertTrue(board.tiles[(j,i)] is not None)
