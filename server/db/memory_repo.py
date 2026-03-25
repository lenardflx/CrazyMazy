from __future__ import annotations

import random
from uuid import UUID, uuid4

from server.db.repo import GameRepository, PlayerRepository, TileRepository, TreasureRepository
from shared.models import GameData, PlayerColor, PlayerData, TileData, TreasureData


class GameRepositoryInMemory(GameRepository):
    def __init__(self) -> None:
        self._games: dict[UUID, GameData] = {}
        self._game_ids_by_code: dict[str, UUID] = {}

    def find_by_game_id(self, game_id: UUID) -> GameData | None:
        return self._games.get(game_id)

    def find_by_join_code(self, join_code: str) -> GameData | None:
        game_id = self._game_ids_by_code.get(join_code)
        if game_id is None:
            return None
        return self._games.get(game_id)

    def create_game(self, board_size: int, leader_player_id: UUID) -> GameData:
        game = GameData(
            code=self._new_code(),
            leader_player_id=leader_player_id,
            board_size=board_size,
        )
        self._games[game.id] = game
        self._game_ids_by_code[game.code] = game.id
        return game

    def delete_game(self, game_id: UUID) -> None:
        game = self._games.pop(game_id, None)
        if game is not None:
            self._game_ids_by_code.pop(game.code, None)

    def update_game(self, new_game: GameData) -> GameData:
        existing = self._games.get(new_game.id)
        if existing is not None and existing.code != new_game.code:
            self._game_ids_by_code.pop(existing.code, None)
        self._games[new_game.id] = new_game
        self._game_ids_by_code[new_game.code] = new_game.id
        return new_game

    def _new_code(self) -> str:
        while True:
            code = f"{random.randint(0, 9999):04d}"
            if code not in self._game_ids_by_code:
                return code


class PlayerRepositoryInMemory(PlayerRepository):
    def __init__(self) -> None:
        self._players: dict[UUID, PlayerData] = {}

    def create_player(
        self,
        display_name: str,
        connection_id: str,
        game_id: UUID,
        join_order: int,
        piece_color: PlayerColor,
        user_id: UUID | None = None,
    ) -> PlayerData:
        player = PlayerData(
            user_id=user_id or uuid4(),
            game_id=game_id,
            connection_id=connection_id,
            display_name=display_name,
            join_order=join_order,
            piece_color=piece_color,
        )
        self._players[player.id] = player
        return player

    def find_by_id(self, player_id: UUID) -> PlayerData | None:
        return self._players.get(player_id)

    def find_by_connection_id(self, connection_id: str) -> PlayerData | None:
        for player in self._players.values():
            if player.connection_id == connection_id:
                return player
        return None

    def list_by_game_id(self, game_id: UUID) -> list[PlayerData]:
        return [player for player in self._players.values() if player.game_id == game_id]

    def update_player(self, player: PlayerData) -> PlayerData:
        self._players[player.id] = player
        return player


class TileRepositoryInMemory(TileRepository):
    def __init__(self) -> None:
        self._tiles: dict[UUID, TileData] = {}

    def create_tile(self, tile: TileData) -> TileData:
        self._tiles[tile.id] = tile
        return tile

    def find_by_id(self, tile_id: UUID) -> TileData | None:
        return self._tiles.get(tile_id)

    def list_by_game_id(self, game_id: UUID) -> list[TileData]:
        return [tile for tile in self._tiles.values() if tile.game_id == game_id]

    def update_tile(self, tile: TileData) -> TileData:
        self._tiles[tile.id] = tile
        return tile

    def delete_tile(self, tile_id: UUID) -> None:
        self._tiles.pop(tile_id, None)


class TreasureRepositoryInMemory(TreasureRepository):
    def __init__(self) -> None:
        self._treasures: dict[UUID, TreasureData] = {}

    def create_treasure(self, treasure: TreasureData) -> TreasureData:
        self._treasures[treasure.id] = treasure
        return treasure

    def find_by_id(self, treasure_id: UUID) -> TreasureData | None:
        return self._treasures.get(treasure_id)

    def list_by_player_id(self, player_id: UUID) -> list[TreasureData]:
        return [treasure for treasure in self._treasures.values() if treasure.player_id == player_id]

    def update_treasure(self, treasure: TreasureData) -> TreasureData:
        self._treasures[treasure.id] = treasure
        return treasure

    def delete_treasure(self, treasure_id: UUID) -> None:
        self._treasures.pop(treasure_id, None)
