# Author: Lukas Saur-Brosch, Tamay Engin

from server.db.sql_repo import TileRepositorySQL
from server.db.engine import create_engine_for_environment
from shared.models import TileData, TileType
from uuid import uuid4

def create_tile_data():
    tile = TileData(
        game_id=uuid4(),
        row=0,
        column=0,
        rotation=1,
        is_spare=False,
        tile_type=TileType.CORNER,
    )
    return tile

def test_create_tile():
    tile_repository = TileRepositorySQL(create_engine_for_environment("test"))
    tile = tile_repository.create_tile(create_tile_data())
    result = tile_repository.find_by_id(tile.id)
    assert result is not None
    assert result.id == tile.id

def test_find_tile_by_id():
    tile_repository = TileRepositorySQL(create_engine_for_environment("test"))
    tile = tile_repository.create_tile(create_tile_data())
    result = tile_repository.find_by_id(tile.id)
    assert result is not None
    assert result.id == tile.id

def test_update_tile():
    tile_repository = TileRepositorySQL(create_engine_for_environment("test"))
    tile = tile_repository.create_tile(create_tile_data())
    tile.row = 1
    tile = tile_repository.update_tile(tile)
    result = tile_repository.find_by_id(tile.id)
    assert result is not None
    assert result.row == 1

def test_delete_tile():
    tile_repository = TileRepositorySQL(create_engine_for_environment("test"))
    tile = tile_repository.create_tile(create_tile_data())
    tile_repository.delete_tile(tile.id)
    result = tile_repository.find_by_id(tile.id)
    assert result is None

def test_list_by_game_id():
    tile_repository = TileRepositorySQL(create_engine_for_environment("test"))
    tile = tile_repository.create_tile(create_tile_data())
    results = tile_repository.list_by_game_id(tile.game_id)
    assert len(results) == 1
    assert results[0].id == tile.id
