# Author: Tamay Engin

from server.db.sql_repo import TreasureRepositorySQL
from server.db.engine import create_engine_for_environment
from shared.models import TreasureType, TreasureData
from uuid import uuid4

def create_treasure_data():
    return TreasureData(
        player_id=uuid4(),
        treasure_type=TreasureType.BOOK,
        order_index=0
    )

def test_create_treasure():
    treasure_repository_sql = TreasureRepositorySQL(create_engine_for_environment("test"))
    treasure = treasure_repository_sql.create_treasure(create_treasure_data())
    result = treasure_repository_sql.find_by_id(treasure.id)
    assert result is not None
    assert result.id == treasure.id

def test_find_by_id():
    treasure_repository_sql = TreasureRepositorySQL(create_engine_for_environment("test"))
    treasure = treasure_repository_sql.create_treasure(create_treasure_data())
    result = treasure_repository_sql.find_by_id(treasure.id)
    assert result is not None
    assert result.id == treasure.id

def test_list_by_player_id():
    treasure_repository_sql = TreasureRepositorySQL(create_engine_for_environment("test"))
    treasure = treasure_repository_sql.create_treasure(create_treasure_data()) 
    results = treasure_repository_sql.list_by_player_id(treasure.player_id)
    assert len(results) == 1
    assert results[0].id == treasure.id

def test_update_treasure():
    treasure_repository_sql = TreasureRepositorySQL(create_engine_for_environment("test"))
    treasure = treasure_repository_sql.create_treasure(create_treasure_data())
    treasure.order_index = 1
    treasure_repository_sql.update_treasure(treasure)
    result = treasure_repository_sql.find_by_id(treasure.id)
    assert result is not None
    assert result.order_index == 1

def test_delete_treasure():
    treasure_repository_sql = TreasureRepositorySQL(create_engine_for_environment("test"))
    treasure = treasure_repository_sql.create_treasure(create_treasure_data())
    treasure_repository_sql.delete_treasure(treasure.id)
    result = treasure_repository_sql.find_by_id(treasure.id)
    assert result is None
