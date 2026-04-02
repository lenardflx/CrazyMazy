from shared.game.board import Board
from shared.game.tile import Tile
from shared.types.enums import TileOrientation, TileType, TreasureType
import unittest
from random import randint

class TestCreateBoard(unittest.TestCase):

    def _randomBoard(self):
        #board = Board(randint(3,8)*2 + 1)
        board = Board(9)
        board.create_board()
        return board

    def test_corners(self):
        # tests if corner have the correct type and colour
        board = self._randomBoard()
        self.assertTrue(board.tiles[(0,0)].type == TileType.CORNER and board.tiles[(0,0)].orientation == TileOrientation.EAST) # top left
        self.assertTrue(board.tiles[(board.width-1, 0)].type == TileType.CORNER and board.tiles[(board.width-1, 0)].orientation == TileOrientation.SOUTH) #top right
        self.assertTrue(board.tiles[(0, board.width-1)].type == TileType.CORNER and board.tiles[(0, board.width-1)].orientation == TileOrientation.NORTH) # bottom left
        self.assertTrue(board.tiles[(board.width-1, board.width-1)].type == TileType.CORNER and board.tiles[(board.width-1, board.width-1)].orientation == TileOrientation.WEST) # bottom right


    def test_fixed_tiles_number(self):
        # tests if all fixed tiles are placed on the board
        board = self._randomBoard()
        counter = 0
        for key in board.tiles:
            if board.tiles[key] is not None:
                counter += 1
        self.assertEqual(counter, ((board.width // 2) + 1)**2)

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
        self.assertEqual(counter, 24)

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

    def test_pathfinding(self):
        board = Board(7)
        board.create_blocked_board()
        coordinates = []
        # straight line from left to right
        for i in range(board.width):
            board.change_tile(i,3, Tile(TileType.STRAIGHT, TileOrientation.EAST))
            coordinates.append((i,3))
        # straight line from middle to bottom
        for i in range(4, 7):
            board.change_tile(4, i, Tile(TileType.STRAIGHT, TileOrientation.NORTH))
            coordinates.append((4, i))
        # t-piece in the middle
        board.change_tile(4,3, Tile(TileType.T, TileOrientation.SOUTH))
        path, _ = board.pathfind((4,3))
        path.sort()
        coordinates.sort()
        self.assertTrue(path == coordinates)
