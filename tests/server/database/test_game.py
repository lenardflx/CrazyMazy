# Author: Tamay Engin

from server.db.sql_repo.py import GameRepositorySQL
from server.db.sql_repo.py import PlayerRepositorySQL

def test_find_game_by_id()
    player = PlayerRepositorySQL.create_player(display_name: "Name")
    game = GameRepositorySQL.create_game(7, player.id)
    results = GameRepositorySQL.find_game_by_id(game.id)
    assert game == results[0]

def test_create_game()
    player = PlayerRepositorySQL.create_player(display_name: "Name")
    game = GameRepositorySQL.create_game(5, player.id)
    results = GameRepositorySQL.find_game_by_id(game.id)
    assert game == results[0]

def test_delete_game()
    player = PlayerRepositorySQL.create_player(display_name: "Name")
    game = GameRepositorySQL.create_game(9, player.id)
    GameRepositorySQL.delete_game(game.id):
    results = GameRepositorySQL.find_game_by_id(game.id)
    assert not results[0].contains(game)

def test_update_game()
    player = PlayerRepositorySQL.create_player(display_name: "Name")
    game = GameRepositorySQL.create_game(11, player.id)
    game.board_size = 13
    GameRepositorySQL.update_game(game)
    results = GameRepositorySQL.find_game_by_id(game.id)
    assert game == results[0]

def test_find_by_join_code()
    player = PlayerRepositorySQL.create_player(display_name: "Name")
    game = GameRepositorySQL.create_game(7, player.id)
    results = GameRepositorySQL.find_by_join_code(game.join_code)
    assert game == results[0]

def test_game():
    test_create_game()
    test_find_game_by_id()
    test_find_by_join_code()
    test_update_game()
    test_delete_game()
