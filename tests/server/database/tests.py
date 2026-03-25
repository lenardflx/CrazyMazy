# Author: Tamay Engin, Lukas Saur-Brosch

from tests.server.database.test_player import test_player
from tests.server.database.test_game import test_game


def run_tests():
    test_player()
    test_game()
