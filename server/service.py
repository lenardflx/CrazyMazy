# Author: Lenard Felix

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from server.db.repo import GameRepository, PlayerRepository
from server.lib.game import can_join_game, is_valid_board_size, normalize_join_code
from server.lib.player import (
    active_players,
    is_display_name_taken,
    is_valid_display_name,
    next_available_color,
    next_join_order,
    normalize_display_name,
)
from shared.models import GameData, GameEndReason, GamePhase, PlayerData, PlayerResult, PlayerStatus, utcnow


@dataclass(slots=True)
class GameState:
    game: GameData
    players: list[PlayerData]


@dataclass(slots=True)
class ConnectionState:
    game: GameData
    player: PlayerData


class GameService:
    def __init__(self, game_repo: GameRepository, player_repo: PlayerRepository) -> None:
        self.game_repo = game_repo
        self.player_repo = player_repo

    def create_lobby(
        self,
        board_size: int,
        leader_display_name: str,
        connection_id: str,
    ) -> ConnectionState:
        if not is_valid_board_size(board_size):
            raise ValueError(f"Invalid board size: {board_size}")

        game = self.game_repo.create_game(board_size)
        leader = self._create_player_for_game(
            game=game,
            display_name=leader_display_name,
            connection_id=connection_id,
        )

        game.leader_player_id = leader.id
        game = self.game_repo.update_game(game)
        return ConnectionState(game=game, player=leader)

    def join_game(
        self,
        join_code: str,
        display_name: str,
        connection_id: str,
    ) -> ConnectionState:
        game = self.find_game_by_code(join_code)
        if game is None:
            raise ValueError(f"Game is not joinable: {join_code!r}")

        players = self.player_repo.list_by_game_id(game.id)
        if not can_join_game(game, players):
            raise ValueError(f"Game is not joinable: {join_code!r}")

        player = self._create_player_for_game(
            game=game,
            display_name=display_name,
            connection_id=connection_id,
        )
        return ConnectionState(game=game, player=player)

    def find_game(self, game_id: UUID) -> GameData | None:
        return self.game_repo.find_by_game_id(game_id)

    def find_game_by_code(self, join_code: str) -> GameData | None:
        return self.game_repo.find_by_join_code(normalize_join_code(join_code))

    def get_game_state(self, game_id: UUID) -> GameState | None:
        game = self.find_game(game_id)
        if game is None:
            return None

        return GameState(game=game, players=self.player_repo.list_by_game_id(game.id))

    def get_connection_state(self, connection_id: str) -> ConnectionState | None:
        player = self.player_repo.find_by_connection_id(connection_id)
        if player is None:
            return None

        game = self.game_repo.find_by_game_id(player.game_id)
        if game is None:
            return None

        return ConnectionState(game=game, player=player)

    def leave_game(self, player_id: UUID) -> GameState | None:
        player = self.player_repo.find_by_id(player_id)
        if player is None:
            return None

        game = self.game_repo.find_by_game_id(player.game_id)
        if game is None:
            return None

        players = self._mark_player_departed(player)

        return self._after_player_departure(game, player, players)

    def give_up(self, player_id: UUID) -> GameState | None:
        player = self.player_repo.find_by_id(player_id)
        if player is None:
            return None

        game = self.game_repo.find_by_game_id(player.game_id)
        if game is None:
            return None

        if player.result == PlayerResult.NONE:
            player.result = PlayerResult.FORFEITED
            self.player_repo.update_player(player)

        players = self._mark_player_departed(player)
        return self._after_player_departure(game, player, players)

    def _after_player_departure(
        self,
        game: GameData,
        player: PlayerData,
        players: list[PlayerData],
    ) -> GameState | None:
        remaining_players = active_players(players)

        if game.game_phase == GamePhase.GAME and len(remaining_players) < 2:
            game.game_phase = GamePhase.POSTGAME
            game.end_reason = GameEndReason.PLAYERS_LEFT
            game.current_player_id = None
            game.ended_at = utcnow()
            game = self.game_repo.update_game(game)
            return GameState(game=game, players=players)

        if not remaining_players:
            self.game_repo.delete_game(game.id)
            return None

        if game.leader_player_id == player.id:
            next_leader = min(remaining_players, key=lambda current: current.join_order)
            game.leader_player_id = next_leader.id
            game = self.game_repo.update_game(game)

        return GameState(game=game, players=players)

    def _mark_player_departed(self, player: PlayerData) -> list[PlayerData]:
        if player.status != PlayerStatus.DEPARTED:
            player.status = PlayerStatus.DEPARTED
            player.connection_id = None
            player.left_at = utcnow()
            self.player_repo.update_player(player)

        return self.player_repo.list_by_game_id(player.game_id)

    def _create_player_for_game(
        self,
        game: GameData,
        display_name: str,
        connection_id: str,
    ) -> PlayerData:
        players = self.player_repo.list_by_game_id(game.id)
        if not is_valid_display_name(display_name):
            raise ValueError(f"Invalid display name: {display_name!r}")
        if is_display_name_taken(players, display_name):
            raise ValueError(f"Display name already taken: {display_name!r}")

        join_order = next_join_order(players)
        piece_color = next_available_color(players)
        if piece_color is None:
            raise ValueError("No player color available")

        return self.player_repo.create_player(
            display_name=normalize_display_name(display_name),
            connection_id=connection_id,
            game_id=game.id,
            join_order=join_order,
            piece_color=piece_color,
        )


# TODO: Add gameplay-oriented services for tiles and treasures once turn flow exists.
