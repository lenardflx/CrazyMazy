import random
import uuid
from typing import Optional
from uuid import UUID


from server.db import GameRepository
from server.db.repo import PlayerRepository
from shared.models import GameData


class GameRepositoryInMemory(GameRepository):
    games = []

    def create_game(self, leader_player_id: UUID, board_size: int) -> Optional[GameData]:
        game = GameData(code=str(random.randint(1000, 9999)), insertion_side=1, leader_player_id=leader_player_id, board_size=board_size)
        game.insertion_side = 3
        self.games.append(game)

class PlayerRepositoryInMemory(PlayerRepository):
    ...