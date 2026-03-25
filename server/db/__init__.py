from server.db.memory_repo import (
    GameRepositoryInMemory,
    PlayerRepositoryInMemory,
    TileRepositoryInMemory,
    TreasureRepositoryInMemory,
)
from server.service import GameService

game_repository = GameRepositoryInMemory()
player_repository = PlayerRepositoryInMemory()
tile_repository = TileRepositoryInMemory()
treasure_repository = TreasureRepositoryInMemory()

game_service = GameService(game_repository, player_repository, tile_repository, treasure_repository)
