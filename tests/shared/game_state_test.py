from shared.state.game_state import Board,TileType, Tile, TreasureType, TileOrientation
import unittest
from random import randint

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

    def test_treasures(self):
        # tests if there are enough treasures on the board and that they are all diffrent
        board = self._randomBoard()
        board.fill_board()
        treasures = []
        counter = 0
        for i in range(board.width):
            for j in range(board.width):
                    if board.tiles[(j,i)].treasure is not None:
                        counter += 1
                        self.assertTrue(board.tiles[(j,i)].treasure not in treasures)
        if board.spare.treasure is not None:
            counter += 1
            self.assertTrue(board.spare.treasure not in treasures)
        self.assertEqual(counter, 28)

    def test_insertion(self):
        board = self._randomBoard()
        board.fill_board()

        # horizontal from the left
        order = []
        y =  randint(1, board.width // 2) * 2 - 1
        for i in range(board.width):
            order.append(board.tiles[(i,y)])
        board.insert_tile(0, y)
        for i in range(1, board.width):
            self.assertTrue(board.tiles[i,y] == order[i-1])
        self.assertTrue(order[board.width-1] == board.spare)
        # horizontal from the right
        order = []
        y = randint(1, board.width // 2) * 2 - 1
        for i in range(board.width):
            order.append(board.tiles[(i, y)])
        board.insert_tile(board.width-1, y)
        for i in range(board.width-2):
            self.assertTrue(board.tiles[i, y] == order[i+1])
        self.assertTrue(order[0] == board.spare)

        # vertical from the top
        order = []
        x = randint(1, board.width // 2) * 2 - 1
        for i in range(board.width):
            order.append(board.tiles[(x, i)])
        board.insert_tile(x, 0)
        for i in range(1, board.width):
            self.assertTrue(board.tiles[x, i] == order[i - 1])
        self.assertTrue(order[board.width - 1] == board.spare)
        # vertical from the bottom
        order = []
        x = randint(1, board.width // 2) * 2 - 1
        for i in range(board.width):
            order.append(board.tiles[(x, i)])
        board.insert_tile(x, board.width-1)
        for i in range(board.width-2):
            self.assertTrue(board.tiles[x, i] == order[i + 1])
        self.assertTrue(order[0] == board.spare)