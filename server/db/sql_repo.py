from uuid import UUID

from server.db import GameRepository
from server.db.repo import PlayerRepository
from shared.models.models import Game


class GameRepositorySQL(GameRepository):
    def find_by_game_id(self, game_id: UUID) -> Game: ...

class PlayerRepositorySQL(PlayerRepository):
    ...