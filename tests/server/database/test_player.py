# Author: Tamay Engin

from server.db.sql_repo import PlayerRepositorySQL
from shared.models import PlayerColor
from uuid import UUID, uuid4

def test_create_player():
    player_repository_sql = PlayerRepositorySQL()
    player = player_repository_sql.create_player("Name", uuid4(), uuid4(), 0, PlayerColor.BLUE, uuid4())
    results = player_repository_sql.find_by_id(player.id)
    assert player == results[0]

def test_find_player_by_id():
    player_repository_sql = PlayerRepositorySQL()
    player = player_repository_sql.create_player("Name", uuid4(), uuid4(), 0, PlayerColor.BLUE, uuid4())
    results = player_repository_sql.find_by_id(player.id)
    assert player == results[0]

def test_update_player():
    player_repository_sql = PlayerRepositorySQL()
    player = player_repository_sql.create_player("Name", uuid4(), uuid4(), 0, PlayerColor.BLUE, uuid4())
    player.display_name = "New_Name"
    player = player_repository_sql.update_player(player)
    results = player_repository_sql.find_by_id(player.id)
    assert results[0].display_name == player.display_name

def test_player():
    test_create_player()
    test_find_player_by_id()
    test_update_player()
    print("tests for player model successful")
