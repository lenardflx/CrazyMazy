# Author: Tamay Engin, Lukas Saur-Brosch

from server.db.sql_repo import PlayerRepositorySQL
from server.db.engine import create_engine_for_environment
from shared.models import PlayerColor
from uuid import uuid4

def test_create_player():
    player_repository_sql = PlayerRepositorySQL(create_engine_for_environment("test"))
    player = player_repository_sql.create_player("Name", f"{uuid4()}", uuid4(), 0, PlayerColor.BLUE)
    result = player_repository_sql.find_by_id(player.id)
    assert result is not None
    assert player.id == result.id

def test_find_player_by_id():
    player_repository_sql = PlayerRepositorySQL(create_engine_for_environment("test"))
    player = player_repository_sql.create_player("Name",f"{uuid4()}", uuid4(), 0, PlayerColor.BLUE)
    result = player_repository_sql.find_by_id(player.id)
    assert result is not None
    assert player.id == result.id

def test_update_player():
    player_repository_sql = PlayerRepositorySQL(create_engine_for_environment("test"))
    player = player_repository_sql.create_player("Name", f"{uuid4()}", uuid4(), 0, PlayerColor.BLUE)
    player.display_name = "New_Name"
    player = player_repository_sql.update_player(player)
    result = player_repository_sql.find_by_id(player.id)
    assert result is not None
    assert result.display_name == player.display_name
