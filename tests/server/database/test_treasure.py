# Author: Tamay Engin

from server.db.sql_repo.py import TreasureRepositorySQL

# treasure_data = 

def test_create_treasure():
    treasure = TreasureRepositorySQL.create_treasure(treasure_data)
    results = TreasureRepositorySQL.find_by_id(treasure.id)
    assert results[0] == treasure

def test_find_by_id():
    treasure = TreasureRepositorySQL.create_treasure(treasure_data)
    results = TreasureRepositorySQL.find_by_id(treasure.id)
    assert results[0] == treasure

def test_list_by_player_id():
    treasure = TreasureRepositorySQL.create_treasure(treasure_data) 
    results = TreasureRepositorySQL.list_by_player_id(treasure.player_id)
    assert results[0] == treasure

def test_update_treasure():
    treasure = TreasureRepositorySQL.create_treasure(treasure_data)
    treasure.order_index = 0
    TreasureRepositorySQL.update_treasure(treasure)
    results = TreasureRepositorySQL.find_by_id(treasure.id)
    assert results[0] == treasure

def test_delete_treasure():
    treasure = TreasureRepositorySQL.create_treasure(treasure_data)
    TreasureRepositorySQL.delete_treasure(treasure.id)
    results = TreasureRepositorySQL.find_by_id(treasure.id)
    assert len(results) < 1

def test_treasure():
    test_find_by_id()
    test_list_by_player_id()
    test_update_treasure()
    test_delete_treasure()
