from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from shared.game.board import Board
from shared.types.data import GameData, PlayerData, TileData, TreasureData


@dataclass(slots=True)
class GameState:
    """Runtime aggregate built from persisted game, player, tile and treasure data."""

    game: GameData
    players: list[PlayerData]
    board: Board | None
    treasures_by_player: dict[UUID, list[TreasureData]]

    @property
    def tiles(self) -> list[TileData]:
        if self.board is None:
            return []
        return self.board.to_tile_data(self.game.id)

    @classmethod
    def from_models(
        cls,
        game: GameData,
        players: list[PlayerData],
        tiles: list[TileData],
        treasures_by_player: dict[UUID, list[TreasureData]],
    ) -> "GameState":
        return cls(
            game=game,
            players=players,
            board=Board.from_tile_data(game, tiles) if tiles else None,
            treasures_by_player=treasures_by_player,
        )
