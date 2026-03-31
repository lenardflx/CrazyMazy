import unittest
from shared.game.npc import Npc, NpcTurn
from shared.game.board import Board
from shared.types.enums import InsertionSide, NpcDifficulty
from uuid import UUID, uuid4
from random import randint

class TestCreateBoard(unittest.TestCase):

    def _randomBoard(self):
        # board = Board(randint(3,8)*2 + 1)
        board = Board(7)
        board.create_board()
        board.fill_board()
        return board

    def test_npc_choose_turn(self):
        npc = Npc(uuid4(), NpcDifficulty.NORMAL)
        move = npc.choose_turn(self._randomBoard(), (2,3), (4,5), InsertionSide.RIGHT, 3)
        print(move)