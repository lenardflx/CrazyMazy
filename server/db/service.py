from typing import Optional
from uuid import UUID

from server.db import GameRepository
from server.db.repo import PlayerRepository
from shared.models import GamePhase, GameData


class PlayerService:
    def __init__(self, player_repo: PlayerRepository):
        self.player_repo = player_repo



class GameService:
    def __init__(self, game_repo: GameRepository):
        self.game_repo = game_repo

    def find_joinable_game(self, join_code: str) -> Optional[GameData]:
        """
        Finds a game with the given join code and checks whether it currently
        accepts

        :param join_code:
        :return:
        """
        game = self.game_repo.find_by_join_code(join_code)
        if game is not None and game.game_phase == GamePhase.PREGAME:
            return game
        return None

