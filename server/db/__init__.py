from server.db.memory_repo import (
    GameRepositoryInMemory,
    PlayerRepositoryInMemory,
)
from server.db.service import GameService

game_repository = GameRepositoryInMemory()
player_repository = PlayerRepositoryInMemory()

game_service = GameService(game_repository, player_repository)
