# Author: Lenard Felix
# TODO: Create Lib helper and add documentation. REVIEW afterwards, since logic critial

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from server.db.repo import GameRepository, PlayerRepository, TileRepository, TreasureRepository
from shared.lib.board import (
    assign_treasures,
    create_board_tiles,
    is_valid_insertion_index,
    opposite_side,
    reachable_positions,
    shift_player_position,
    shift_tiles,
    split_board_tiles,
    start_position_for_color,
)
from shared.lib.lobby import MIN_STARTABLE_PLAYERS
from server.lib.game import can_join_game, is_valid_board_size, normalize_join_code
from server.lib.player import (
    active_players,
    is_display_name_taken,
    is_valid_display_name,
    next_available_color,
    next_join_order,
    normalize_display_name,
)
from shared.models import (
    GameData,
    GameEndReason,
    GamePhase,
    InsertionSide,
    PlayerData,
    PlayerResult,
    PlayerStatus,
    TileData,
    TreasureType,
    TreasureData,
    TurnPhase,
    utcnow,
)


@dataclass(slots=True)
class GameState:
    game: GameData
    players: list[PlayerData]
    tiles: list[TileData]
    treasures_by_player: dict[UUID, list[TreasureData]]


@dataclass(slots=True)
class ConnectionState:
    game: GameData
    player: PlayerData


class GameService:
    def __init__(
        self,
        game_repo: GameRepository,
        player_repo: PlayerRepository,
        tile_repo: TileRepository,
        treasure_repo: TreasureRepository,
    ) -> None:
        self.game_repo = game_repo
        self.player_repo = player_repo
        self.tile_repo = tile_repo
        self.treasure_repo = treasure_repo

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
        game.revision += 1
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
        game.revision += 1
        self.game_repo.update_game(game)
        return ConnectionState(game=game, player=player)

    def find_game(self, game_id: UUID) -> GameData | None:
        return self.game_repo.find_by_game_id(game_id)

    def find_game_by_code(self, join_code: str) -> GameData | None:
        return self.game_repo.find_by_join_code(normalize_join_code(join_code))

    def get_game_state(self, game_id: UUID) -> GameState | None:
        game = self.find_game(game_id)
        if game is None:
            return None

        players = self.player_repo.list_by_game_id(game.id)
        tiles = self.tile_repo.list_by_game_id(game.id)
        treasures_by_player = {player.id: self.treasure_repo.list_by_player_id(player.id) for player in players}
        return GameState(game=game, players=players, tiles=tiles, treasures_by_player=treasures_by_player)

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

    def start_game(self, player_id: UUID) -> GameState:
        player = self.player_repo.find_by_id(player_id)
        if player is None:
            raise ValueError("Player not found")

        game = self.game_repo.find_by_game_id(player.game_id)
        if game is None:
            raise ValueError("Game not found")
        if game.leader_player_id != player.id:
            raise ValueError("Only the leader can start the game")
        if game.game_phase not in (GamePhase.PREGAME, GamePhase.POSTGAME):
            raise ValueError("Game cannot be started right now")

        players = self.player_repo.list_by_game_id(game.id)
        active = sorted(active_players(players), key=lambda current: current.join_order)
        if len(active) < MIN_STARTABLE_PLAYERS:
            raise ValueError("Not enough players to start the game")

        self._clear_game_runtime(game.id, players)
        self._create_runtime_board(game)
        self._assign_treasures(active)

        for current in players:
            if current.status == PlayerStatus.DEPARTED:
                current.position_x = None
                current.position_y = None
                self.player_repo.update_player(current)
                continue
            start_x, start_y = start_position_for_color(game.board_size, current.piece_color)
            current.position_x = start_x
            current.position_y = start_y
            current.result = PlayerResult.NONE
            current.placement = None
            current.finished_at = None
            self.player_repo.update_player(current)

        game.game_phase = GamePhase.GAME
        game.end_reason = None
        game.turn_phase = TurnPhase.SHIFT
        game.current_player_id = active[0].id
        game.blocked_insertion_side = None
        game.blocked_insertion_index = None
        game.started_at = utcnow()
        game.ended_at = None
        game.revision += 1
        game = self.game_repo.update_game(game)
        state = self.get_game_state(game.id)
        if state is None:
            raise ValueError("Game not found")
        return state

    def shift_tile(self, player_id: UUID, side: InsertionSide, index: int, rotation: int) -> GameState:
        player, game = self._require_current_player(player_id, TurnPhase.SHIFT)
        if not is_valid_insertion_index(game.board_size, index):
            raise ValueError(f"Invalid insertion index: {index}")
        if game.blocked_insertion_side == side and game.blocked_insertion_index == index:
            raise ValueError("That insertion is blocked")

        state = self.get_game_state(game.id)
        if state is None:
            raise ValueError("Game not found")
        tiles = state.tiles
        shift_tiles(
            tiles,
            board_size=game.board_size,
            side=side,
            index=index,
            rotation=rotation,
        )
        for tile in tiles:
            self.tile_repo.update_tile(tile)

        for current in state.players:
            shifted = shift_player_position(
                self._player_position(current),
                board_size=game.board_size,
                side=side,
                index=index,
            )
            if shifted is None:
                continue
            current.position_x, current.position_y = shifted
            self.player_repo.update_player(current)

        game.turn_phase = TurnPhase.MOVE
        game.blocked_insertion_side = opposite_side(side)
        game.blocked_insertion_index = index
        game.revision += 1
        game = self.game_repo.update_game(game)
        updated = self.get_game_state(game.id)
        if updated is None:
            raise ValueError("Game not found")
        return updated

    def move_player(self, player_id: UUID, x: int, y: int) -> GameState:
        player, game = self._require_current_player(player_id, TurnPhase.MOVE)
        state = self.get_game_state(game.id)
        if state is None:
            raise ValueError("Game not found")
        board, _ = split_board_tiles(state.tiles)
        start = self._player_position(player)
        if start is None:
            raise ValueError("Player has no position")
        destination = (x, y)
        if destination not in reachable_positions(board, start):
            raise ValueError("Target position is not reachable")

        player.position_x = x
        player.position_y = y
        self.player_repo.update_player(player)
        self._collect_treasure_if_present(player, board[destination].treasure_type)
        if self._player_has_won(game, player):
            player.result = PlayerResult.WON
            player.placement = 1
            player.finished_at = utcnow()
            self.player_repo.update_player(player)
            game.game_phase = GamePhase.POSTGAME
            game.end_reason = GameEndReason.COMPLETED
            game.current_player_id = None
            game.turn_phase = None
            game.ended_at = utcnow()
        game.revision += 1
        game = self.game_repo.update_game(game)
        updated = self.get_game_state(game.id)
        if updated is None:
            raise ValueError("Game not found")
        if updated.game.game_phase == GamePhase.POSTGAME:
            return updated
        return self._finish_move(updated.game, player)

    def end_turn(self, player_id: UUID) -> GameState:
        player, game = self._require_current_player(player_id, TurnPhase.MOVE)
        return self._finish_move(game, player)

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
            game.turn_phase = None
            game.ended_at = utcnow()
            if len(remaining_players) == 1:
                winner = remaining_players[0]
                winner.result = PlayerResult.WON
                winner.placement = 1
                winner.finished_at = utcnow()
                self.player_repo.update_player(winner)
            # TODO: Assign placements/results for every player
            game.revision += 1
            game = self.game_repo.update_game(game)
            state = self.get_game_state(game.id)
            return state

        if not remaining_players:
            self.game_repo.delete_game(game.id)
            return None

        if game.current_player_id == player.id and game.game_phase == GamePhase.GAME:
            next_player = self._next_active_player(remaining_players, player.id)
            game.current_player_id = next_player.id
            game.turn_phase = TurnPhase.SHIFT
            game.blocked_insertion_side = None
            game.blocked_insertion_index = None

        if game.leader_player_id == player.id:
            next_leader = min(remaining_players, key=lambda current: current.join_order)
            game.leader_player_id = next_leader.id
        game.revision += 1
        game = self.game_repo.update_game(game)
        state = self.get_game_state(game.id)
        return state

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

    def _finish_move(self, game: GameData, player: PlayerData) -> GameState:
        next_player = self._next_active_player(active_players(self.player_repo.list_by_game_id(game.id)), player.id)
        game.current_player_id = next_player.id
        game.turn_phase = TurnPhase.SHIFT
        game.blocked_insertion_side = None
        game.blocked_insertion_index = None
        game.revision += 1
        game = self.game_repo.update_game(game)
        state = self.get_game_state(game.id)
        if state is None:
            raise ValueError("Game not found")
        return state

    def _require_current_player(self, player_id: UUID, phase: TurnPhase) -> tuple[PlayerData, GameData]:
        player = self.player_repo.find_by_id(player_id)
        if player is None:
            raise ValueError("Player not found")
        game = self.game_repo.find_by_game_id(player.game_id)
        if game is None:
            raise ValueError("Game not found")
        if game.game_phase != GamePhase.GAME:
            raise ValueError("Game is not active")
        if game.current_player_id != player.id:
            raise ValueError("It is not your turn")
        if game.turn_phase != phase:
            raise ValueError(f"Expected turn phase: {phase.value}")
        return player, game

    def _clear_game_runtime(self, game_id: UUID, players: list[PlayerData]) -> None:
        for tile in self.tile_repo.list_by_game_id(game_id):
            self.tile_repo.delete_tile(tile.id)
        for player in players:
            for treasure in self.treasure_repo.list_by_player_id(player.id):
                self.treasure_repo.delete_treasure(treasure.id)

    def _create_runtime_board(self, game: GameData) -> None:
        tiles = create_board_tiles(game.id, game.board_size)
        for tile in tiles:
            self.tile_repo.create_tile(tile)

    def _assign_treasures(self, players: list[PlayerData]) -> None:
        assignments = assign_treasures(len(players))
        for player, treasure_types in zip(players, assignments, strict=False):
            for order_index, treasure_type in enumerate(treasure_types):
                self.treasure_repo.create_treasure(
                    TreasureData(
                        player_id=player.id,
                        treasure_type=treasure_type,
                        order_index=order_index,
                    )
                )

    def _collect_treasure_if_present(self, player: PlayerData, treasure_type: TreasureType | None) -> None:
        if treasure_type is None:
            return
        target = self._active_treasure(player.id)
        if target is None or target.treasure_type != treasure_type:
            return
        target.collected = True
        target.collected_at = utcnow()
        self.treasure_repo.update_treasure(target)

    def _player_has_won(self, game: GameData, player: PlayerData) -> bool:
        if self._active_treasure(player.id) is not None:
            return False
        home_x, home_y = start_position_for_color(game.board_size, player.piece_color)
        return player.position_x == home_x and player.position_y == home_y

    def _active_treasure(self, player_id: UUID) -> TreasureData | None:
        treasures = sorted(self.treasure_repo.list_by_player_id(player_id), key=lambda current: current.order_index)
        for treasure in treasures:
            if not treasure.collected:
                return treasure
        return None

    def _next_active_player(self, players: list[PlayerData], current_player_id: UUID) -> PlayerData:
        ordered = sorted(players, key=lambda current: current.join_order)
        current_index = next((index for index, player in enumerate(ordered) if player.id == current_player_id), -1)
        return ordered[(current_index + 1) % len(ordered)]

    def _player_position(self, player: PlayerData) -> tuple[int, int] | None:
        if player.position_x is None or player.position_y is None:
            return None
        return player.position_x, player.position_y
