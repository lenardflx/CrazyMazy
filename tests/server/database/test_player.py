# Author: Tamay Engin, Lukas Saur-Brosch

from server.db.sql_repo import PlayerRepositorySQL
from server.db.engine import create_engine_for_environment
from shared.types.enums import PlayerColor
from uuid import uuid4

def test_create_player_and_find_by_id():
    """Create an instance of the table Player and raise an AssertionError if the row is not found"""
    player_repository_sql = PlayerRepositorySQL(create_engine_for_environment("test"))
    player = player_repository_sql.create_player("Name", f"{uuid4()}", uuid4(), 0, PlayerColor.BLUE)
    result = player_repository_sql.find_by_id(player.id)
    assert result is not None
    assert player.id == result.id

def list_by_game_id():
    """Create an instance of the table Player and raise an AssertionError if the row is not found using game_id"""
    player_repository_sql = PlayerRepositorySQL(create_engine_for_environment("test"))
    player = player_repository_sql.create_player("Name", f"{uuid4()}", uuid4(), 0, PlayerColor.BLUE)
    results = player_repository_sql.list_by_game_id(player.game_id)
    assert len(results) == 1
    assert results[0].id == player.id

def test_update_player():
    """Create and update an instance of the table Player and raise an AssertionError if the row was not updated in the table"""
    player_repository_sql = PlayerRepositorySQL(create_engine_for_environment("test"))
    player = player_repository_sql.create_player("Name", f"{uuid4()}", uuid4(), 0, PlayerColor.BLUE)
    player.display_name = "New_Name"
    player = player_repository_sql.update_player(player)
    result = player_repository_sql.find_by_id(player.id)
    assert result is not None
    assert result.display_name == player.display_name
