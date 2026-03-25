from uuid import UUID

from server.db import GameRepository
from server.db.repo import PlayerRepository
from shared.models.models import Game


class GameRepositoryInMemory(GameRepository):
    def find_by_game_id(self, game_id: UUID) -> Game:
        print("find_by_game_id in memory")

    def find_by_join_code(self, join_code: str) -> Game: ...

    def create_game(self, board_size: int, leader_player_id: UUID) -> Game: ...

    def delete_game(self, game_id: int): ...

    def update_game(self, new_game: Game): ...

class PlayerRepositoryInMemory(PlayerRepository):
    ...