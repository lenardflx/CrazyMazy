# Author: Raphael Eiden

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from shared.models import GameData, PlayerData, TileData, TreasureData


class GameRepository(ABC):
    """
    An abstraction for all database operations related to Game objects.
    Note that this repository is strictly responsible for direct database
    operations and any business logic or resulting queries are made by the
    Service classes.
    """

    @abstractmethod
    def find_by_game_id(self, game_id: UUID) -> Optional[GameData]:
        """
        Find a game by its unique game id, which is equivalent to
        the primary key (id) of the game entity and may NOT necessarily be
        the (join) code.

        :param game_id: The id of the game entity to look for.
        :return: A GameData object if found, None otherwise.
        """
        ...

    @abstractmethod
    def find_by_join_code(self, join_code: str) -> Optional[GameData]: ...

    @abstractmethod
    def create_game(self, board_size: int, leader_player_id: UUID) -> Optional[GameData]:
        """
        Create a new game entity based on the

        :param board_size:          The width of the board. This must be an odd number
                                    and at least 7 (which is also the default)
        :param leader_player_id:    The id of the player who created the game.
        :return: The GameData entity including the generated data such as primary key (id)
        """
        ...

    @abstractmethod
    def delete_game(self, game_id: UUID):
        """
        Delete a game by its game id.

        :param game_id: The id of the game to delete. This is the primary key (id) and not the join code.
        """
        ...

    @abstractmethod
    def update_game(self, new_game: GameData):
        """
        Updates the given GameData object in the database.
        This method will use the `id` of the game data object
        and apply all values in the object to the entity in the
        database associated with that id.

        :param new_game: The game data to be written into the database.
        """
        ...

class PlayerRepository(ABC):
    """
    An abstraction for all database operations related to Player objects.
    Note that this repository is strictly responsible for direct database
    operations and any business logic or resulting queries are made by the
    Service classes.
    """

    @abstractmethod
    def create_player(self, display_name: str, connection_id: str) -> Optional[PlayerData]: ...

    @abstractmethod
    def find_by_id(self, player_id: UUID) -> Optional[PlayerData]: ...

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
