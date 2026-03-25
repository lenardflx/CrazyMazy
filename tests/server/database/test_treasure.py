# Author: Tamay Engin

from server.db.sql_repo import TreasureRepositorySQL
from shared.models import TreasureType, TreasureData
from uuid import UUID, uuid4

def create_treasure_data():
    treasure_data = TreasureData()
    treasure_data.id = uuid4()
    treasure_data.treasure_type = TreasureType.BOOK
    treasure_data.order_index = 0
    treasure_data.collected = 0
    treasure_data.player_id = uuid4()
    treasure_data.order_index: int = Field(index=True)
    treasure_data.collected = False
    return treasure_data

def test_create_treasure():
    treasure_repository_sql = TreasureRepositorySQL()
    treasure = treasure_repository_sql.create_treasure(create_treasure_data())
    results = treasure_repository_sql.find_by_id(treasure.id)
    assert results[0] == treasure

def test_find_by_id():
    treasure_repository_sql = TreasureRepositorySQL()
    treasure = treasure_repository_sql.create_treasure(create_treasure_data())
    results = treasure_repository_sql.find_by_id(treasure.id)
    assert results[0] == treasure

def test_list_by_player_id():
    treasure_repository_sql = TreasureRepositorySQL()
    treasure = treasure_repository_sql.create_treasure(create_treasure_data()) 
    results = treasure_repository_sql.list_by_player_id(treasure.player_id)
    assert results[0] == treasure

def test_update_treasure():
    treasure_repository_sql = TreasureRepositorySQL()
    treasure = treasure_repository_sql.create_treasure(create_treasure_data())
    treasure.order_index = 0
    treasure_repository_sql.update_treasure(treasure)
    results = treasure_repository_sql.find_by_id(treasure.id)
    assert results[0] == treasure

def test_delete_treasure():
    treasure_repository_sql = TreasureRepositorySQL()
    treasure = treasure_repository_sql.create_treasure(create_treasure_data())
    treasure_repository_sql.delete_treasure(treasure.id)
    results = treasure_repository_sql.find_by_id(treasure.id)
    assert len(results) < 1

def test_treasure():
    test_find_by_id()
    test_list_by_player_id()
    test_update_treasure()
    test_delete_treasure()
    print("tests for treasure model successful")
