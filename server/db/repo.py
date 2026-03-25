from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from shared.models import GameData, PlayerData

class GameRepository(ABC):

    @abstractmethod
    def find_by_game_id(self, game_id: UUID) -> Optional[GameData]: ...

    @abstractmethod
    def find_by_join_code(self, join_code: str) -> Optional[GameData]: ...

    @abstractmethod
    def create_game(self, board_size: int, leader_player_id: UUID) -> Optional[GameData]: ...

    @abstractmethod
    def delete_game(self, game_id: UUID): ...

    @abstractmethod
    def update_game(self, new_game: GameData): ...

class PlayerRepository(ABC):

    @abstractmethod
    def create_player(self, display_name: str, connection_id: str) -> Optional[PlayerData]: ...

    @abstractmethod
    def find_by_id(self, player_id: UUID) -> Optional[PlayerData]: ...

    @abstractmethod
    def update_player(self, player: PlayerData) -> PlayerData: ...