# Author: Tamay Engin, Lukas Saur-Brosch

from server.db.sql_repo import TileRepositorySQL
from server.db.engine import create_engine_for_environment
from shared.models import TileData, TileType
from uuid import uuid4

engine = create_engine_for_environment("test")

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
    tile_repository = TileRepositorySQL(engine)
    tile = tile_repository.create_tile(create_tile_data())
    results = tile_repository.find_by_id(tile.id)
    assert results is not None
    assert results.id == tile.id

def test_find_tile_by_id():
    tile_repository = TileRepositorySQL(engine)
    tile = tile_repository.create_tile(create_tile_data())
    results = tile_repository.find_by_id(tile.id)
    assert results is not None
    assert results.id == tile.id

def test_update_tile():
    tile_repository = TileRepositorySQL(engine)
    tile = tile_repository.create_tile(create_tile_data())
    tile.row = 1
    tile = tile_repository.update_tile(tile)
    results = tile_repository.find_by_id(tile.id)
    assert results is not None
    assert results.id == tile.id

def test_delete_tile():
    tile_repository = TileRepositorySQL(engine)
    tile = tile_repository.create_tile(create_tile_data())
    tile_repository.delete_tile(tile.id)
    results = tile_repository.find_by_id(tile.id)
    assert results is None

def test_list_by_game_id():
    tile_repository = TileRepositorySQL(engine)
    tile = tile_repository.create_tile(create_tile_data())
    results = tile_repository.find_by_id(tile.game_id)
    assert results == tile


def test_tile():
    test_create_tile()
    test_find_tile_by_id()
    test_update_tile()
    test_delete_tile()
    test_list_by_game_id()
    print("tests for player model successful")
