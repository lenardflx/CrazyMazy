# Author: Tamay Engin

from server.db.sql_repo import GameRepositorySQL
from server.db.engine import create_engine_for_environment
from shared.types.enums import GamePhase
from uuid import uuid4

def create_game(game_repository_sql: GameRepositorySQL):
    return game_repository_sql.create_game(
        board_size=7,
        leader_player_id=uuid4(),
        is_public=False,
        player_limit=4,
        insert_timeout=5
    )

def test_create_game_and_find_game_by_id():
    """Create an instance of the table Game and raise an AssertionError if the row is not found"""
    game_repository_sql = GameRepositorySQL(create_engine_for_environment("test"))
    game = create_game(game_repository_sql)
    result = game_repository_sql.find_by_game_id(game.id)
    assert result is not None
    assert game.id == result.id

def test_find_active_games():
    """Create an instance of the table Game, set the game phase to game and raise an AssertionError if the row is not found by looking for active games"""
    game_repository_sql = GameRepositorySQL(create_engine_for_environment("test"))
    game = create_game(game_repository_sql)
    game.game_phase = GamePhase.GAME
    game_repository_sql.update_game(game)
    results = game_repository_sql.find_active_games()
    assert game in results

def test_update_game():
    """Create and update an instance of the table Game and raise an AssertionError if the row was not updated in the table"""
    game_repository_sql = GameRepositorySQL(create_engine_for_environment("test"))
    game = create_game(game_repository_sql)
    game.board_size = 13
    game_repository_sql.update_game(game)
    result = game_repository_sql.find_by_game_id(game.id)
    assert result is not None
    assert result.board_size == 13

def test_delete_game():
    """Create and delete an instance of the table Game and raise an AssertionError if the row is found in the table"""
    game_repository_sql = GameRepositorySQL(create_engine_for_environment("test"))
    game = create_game(game_repository_sql)
    game_repository_sql.delete_game(game.id)
    result = game_repository_sql.find_by_game_id(game.id)
    assert result is None

def test_find_by_join_code():
    """Create an instance of the table Game and raise an AssertionError if the row is not found using join code"""
    game_repository_sql = GameRepositorySQL(create_engine_for_environment("test"))
    game = create_game(game_repository_sql)
    result = game_repository_sql.find_by_join_code(game.code)
    assert result is not None
    assert game.id == result.id
