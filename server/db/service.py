from uuid import UUID

from server.db import GameRepository


class GameService:
    def __init__(self, game_repo: GameRepository):
        self.game_repo = game_repo

    def find_joinable_game(self):
        self.game_repo.find_by_game_id(UUID("a816ab9d-a268-4796-8654-78f4d00ad4fb"))