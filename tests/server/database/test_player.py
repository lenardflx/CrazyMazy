# Author: Tamay Engin

from server.db.sql_repo.py import PlayerRepositorySQL

def test_create_player():
    player = PlayerRepositorySQL.create_player("Name")
    results = PlayerRepositorySQL.find_by_id(player.id)
    assert player == results[0]

def test_find_player_by_id():
    player = PlayerRepositorySQL.create_player("Name")
    results = PlayerRepositorySQL.find_by_id(player.id)
    assert player == results[0]

def test_update_player():
    player = PlayerRepositorySQL.create_player("Name")
    player.display_name = "New_Name"
    player = PlayerRepositorySQL.update_player(player)
    results = PlayerRepositorySQL.find_by_id(player.id)
    assert results[0].display_name == player.display_name

def test_player():
    test_create_player()
    test_find_player_by_id()
    test_update_player()
