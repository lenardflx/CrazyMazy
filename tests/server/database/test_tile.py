# Author: Lukas Saur-Brosch, Tamay Engin

from server.db.sql_repo import TileRepositorySQL
from server.db.engine import create_engine_for_environment
from shared.types.enums import TileType
from shared.types.data import TileData
from uuid import uuid4

def create_tile_data():
    """Creates a tile instance that can be used for testing the repository"""
    tile = TileData(
        game_id=uuid4(),
        row=0,
        column=0,
        rotation=1,
        is_spare=False,
        tile_type=TileType.CORNER,
    )
    return tile

def test_create_tile_and_find_by_id():
    """Create an instance of the table Tile and raise an AssertionError if the row is not found"""
    tile_repository = TileRepositorySQL(create_engine_for_environment("test"))
    tile = tile_repository.create_tile(create_tile_data())
    result = tile_repository.find_by_id(tile.id)
    assert result is not None
    assert result.id == tile.id

def test_update_tile():
    """Create and update an instance of the table Tile and raise an AssertionError if the row was not updated in the table"""
    tile_repository = TileRepositorySQL(create_engine_for_environment("test"))
    tile = tile_repository.create_tile(create_tile_data())
    tile.row = 1
    tile = tile_repository.update_tile(tile)
    result = tile_repository.find_by_id(tile.id)
    assert result is not None
    assert result.row == 1

def test_delete_tile():
    """Create and delete an instance of the table Tile and raise an AssertionError if the row is found in the table"""
    tile_repository = TileRepositorySQL(create_engine_for_environment("test"))
    tile = tile_repository.create_tile(create_tile_data())
    tile_repository.delete_tile(tile.id)
    result = tile_repository.find_by_id(tile.id)
    assert result is None

def test_list_by_game_id():
    """Create an instance of the table Tile and raise an AssertionError if the row is not found using game_id"""
    tile_repository = TileRepositorySQL(create_engine_for_environment("test"))
    tile = tile_repository.create_tile(create_tile_data())
    results = tile_repository.list_by_game_id(tile.game_id)
    assert len(results) == 1
    assert results[0].id == tile.id
