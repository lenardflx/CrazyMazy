from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from shared.game.board import Board
from shared.game.helper import start_position_for_color
from shared.game.npc import Npc
from shared.types.data import GameData, PlayerData, TileData, TreasureData
from shared.types.enums import NpcDifficulty, PlayerControllerKind


@dataclass(slots=True)
class GameState:
    """Runtime aggregate built from persisted game, player, tile and treasure data."""

    game: GameData
    players: list[PlayerData]
    board: Board | None
    treasures_by_player: dict[UUID, list[TreasureData]]
    npcs: dict[UUID, Npc] = field(default_factory=dict)

    def current_treasure(self, player_id: UUID) -> TreasureData | None:
        """Return the next uncollected treasure for a player, or None if all collected."""
        treasures = self.treasures_by_player.get(player_id, [])
        return next(
            (t for t in sorted(treasures, key=lambda t: t.order_index) if not t.collected),
            None,
        )

    def player_by_id(self, player_id: UUID) -> PlayerData | None:
        return next((player for player in self.players if player.id == player_id), None)

    def player_position(self, player_id: UUID) -> tuple[int, int] | None:
        player = self.player_by_id(player_id)
        if player is None:
            raise ValueError(f"Player {player_id} not found in game state")
        if player.position_x is None or player.position_y is None:
            return None
        return player.position_x, player.position_y

    def target_position_for_player(self, player_id: UUID) -> tuple[int, int] | None:
        player = self.player_by_id(player_id)
        if player is None:
            raise ValueError(f"Player {player_id} not found in game state")
        if self.board is None:
            raise ValueError("NPC target requires a board")

        target = self.current_treasure(player_id)
        if target is not None:
            position = next(
                (position for position, tile in self.board.tiles.items() if tile.treasure == target.treasure_type),
                None,
            )
            if position is not None:
                return position
            if self.board.spare is not None and self.board.spare.treasure == target.treasure_type:
                return None
            raise ValueError(f"Target treasure {target.treasure_type} is missing from board and spare tile")

        return start_position_for_color(self.game.board_size, player.piece_color)

    def target_on_spare_for_player(self, player_id: UUID) -> bool:
        if self.board is None:
            raise ValueError("NPC target requires a board")

        target = self.current_treasure(player_id)
        if target is None:
            return False
        if self.board.spare is None:
            raise ValueError("Board has no spare tile")
        return self.board.spare.treasure == target.treasure_type

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
            npcs={
                player.id: Npc(
                    player_id=player.id,
                    difficulty=player.npc_difficulty or NpcDifficulty.NORMAL,
                )
                for player in players
                if player.controller_kind == PlayerControllerKind.NPC
            },
        )
