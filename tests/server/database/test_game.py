# Author: Tamay Engin

from server.db.sql_repo import GameRepositorySQL
from server.db.engine import create_engine_for_environment
from uuid import uuid4

def test_find_game_by_id():
    game_repository_sql = GameRepositorySQL(create_engine_for_environment("test"))
    game = game_repository_sql.create_game(7, uuid4())
    result = game_repository_sql.find_by_game_id(game.id)
    assert result is not None
    assert game.id == result.id

def test_create_game():
    game_repository_sql = GameRepositorySQL(create_engine_for_environment("test"))
    game = game_repository_sql.create_game(5, uuid4())
    result = game_repository_sql.find_by_game_id(game.id)
    assert result is not None
    assert game.id == result.id

def test_delete_game():
    game_repository_sql = GameRepositorySQL(create_engine_for_environment("test"))
    game = game_repository_sql.create_game(9, uuid4())
    game_repository_sql.delete_game(game.id)
    result = game_repository_sql.find_by_game_id(game.id)
    assert result is None

def test_update_game():
    game_repository_sql = GameRepositorySQL(create_engine_for_environment("test"))
    game = game_repository_sql.create_game(11, uuid4())
    game.board_size = 13
    game_repository_sql.update_game(game)
    result = game_repository_sql.find_by_game_id(game.id)
    assert result is not None
    assert result.board_size == 13

def test_find_by_join_code():
    game_repository_sql = GameRepositorySQL(create_engine_for_environment("test"))
    game = game_repository_sql.create_game(7, uuid4())
    result = game_repository_sql.find_by_join_code(game.code)
    assert result is not None
    assert game.id == result.id
