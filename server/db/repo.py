from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from shared.models import GameData, PlayerColor, PlayerData, TileData, TreasureData


class GameRepository(ABC):
    @abstractmethod
    def find_by_game_id(self, game_id: UUID) -> GameData | None: ...

    @abstractmethod
    def find_by_join_code(self, join_code: str) -> GameData | None: ...

    @abstractmethod
    def create_game(self, board_size: int, leader_player_id: UUID) -> GameData: ...

    @abstractmethod
    def delete_game(self, game_id: UUID) -> None: ...

    @abstractmethod
    def update_game(self, new_game: GameData) -> GameData: ...


class PlayerRepository(ABC):
    @abstractmethod
    def create_player(
        self,
        display_name: str,
        connection_id: str,
        game_id: UUID,
        join_order: int,
        piece_color: PlayerColor,
        user_id: UUID | None = None,
    ) -> PlayerData: ...

    @abstractmethod
    def find_by_id(self, player_id: UUID) -> PlayerData | None: ...

    @abstractmethod
    def find_by_connection_id(self, connection_id: str) -> PlayerData | None: ...

    @abstractmethod
    def list_by_game_id(self, game_id: UUID) -> list[PlayerData]: ...

    @abstractmethod
    def update_player(self, player: PlayerData) -> PlayerData: ...


class TileRepository(ABC):
    @abstractmethod
    def create_tile(self, tile: TileData) -> TileData: ...

    @abstractmethod
    def find_by_id(self, tile_id: UUID) -> TileData | None: ...

    @abstractmethod
    def list_by_game_id(self, game_id: UUID) -> list[TileData]: ...

    @abstractmethod
    def update_tile(self, tile: TileData) -> TileData: ...

    @abstractmethod
    def delete_tile(self, tile_id: UUID) -> None: ...


class TreasureRepository(ABC):
    @abstractmethod
    def create_treasure(self, treasure: TreasureData) -> TreasureData: ...

    @abstractmethod
    def find_by_id(self, treasure_id: UUID) -> TreasureData | None: ...

    @abstractmethod
    def list_by_player_id(self, player_id: UUID) -> list[TreasureData]: ...

    @abstractmethod
    def update_treasure(self, treasure: TreasureData) -> TreasureData: ...

    @abstractmethod
    def delete_treasure(self, treasure_id: UUID) -> None: ...
