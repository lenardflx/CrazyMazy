# Author: Tamay Engin

from server.db.sql_repo import GameRepositorySQL
from uuid import UUID, uuid4

def test_find_game_by_id():
    game_repository_sql = GameRepositorySQL()
    game = game_repository_sql.create_game(7, uuid4())
    results = game_repository_sql.find_game_by_id(game.id)
    assert game == results[0]

def test_create_game():
    game_repository_sql = GameRepositorySQL()
    game = game_repository_sql.create_game(5, uuid4())
    results = game_repository_sql.find_game_by_id(game.id)
    assert game == results[0]

def test_delete_game():
    game_repository_sql = GameRepositorySQL()
    game = game_repository_sql.create_game(9, uuid4())
    game_repository_sql.delete_game(game.id)
    results = game_repository_sql.find_game_by_id(game.id)
    assert len(results) < 1

def test_update_game():
    game_repository_sql = GameRepositorySQL()
    game = game_repository_sql.create_game(11, uuid4())
    game.board_size = 13
    game_repository_sql.update_game(game)
    results = game_repository_sql.find_game_by_id(game.id)
    assert game == results[0]

def test_find_by_join_code():
    game_repository_sql = GameRepositorySQL()
    game = game_repository_sql.create_game(7, uuid4())
    results = game_repository_sql.find_by_join_code(game.join_code)
    assert game == results[0]

def test_game():
    test_create_game()
    test_find_game_by_id()
    test_find_by_join_code()
    test_update_game()
    test_delete_game()
    print("tests for game model successful")
