import random
import uuid
from typing import Optional
from uuid import UUID

from server.db import GameRepository
from server.db.repo import PlayerRepository
from shared.models import GameData, PlayerData


class GameRepositoryInMemory(GameRepository):
    games: dict[UUID, GameData] = {}

    def create_game(self, leader_player_id: UUID, board_size: int) -> Optional[GameData]:
        id = uuid.uuid4()
        game = GameData(id=id, code=str(random.randint(1000, 9999)), leader_player_id=leader_player_id, board_size=board_size)
        self.games[id] = game

    def find_by_game_id(self, game_id: UUID) -> Optional[GameData]:
        return self.games.get(game_id, None)

    def find_by_join_code(self, join_code: str) -> Optional[GameData]:
        return next((game for game in self.games.values() if game.code == join_code), None)

    def delete_game(self, game_id: UUID):
        self.games.pop(game_id)

    def update_game(self, new_game: GameData):
        self.games[new_game.id] = new_game

class PlayerRepositoryInMemory(PlayerRepository):
    players: dict[UUID, PlayerData] = {}

    def create_player(self, display_name: str, connection_id: str) -> Optional[PlayerData]:
        id = uuid.uuid4()
        player = PlayerData(id=id, display_name=display_name, connection_id=connection_id)
        self.players[id] = player

    def find_by_id(self, player_id: UUID) -> Optional[PlayerData]:
        return self.players.get(player_id, None)

    def update_player(self, player: PlayerData):
        self.players[player.id] = player