# Author: Lenard Felix
# TODO: Create Lib helper and add documentation. REVIEW afterwards, since logic critial

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from server.db.repo import GameRepository, PlayerRepository, TileRepository, TreasureRepository
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
from shared.state.game_state import GameState, Board, assign_treasures, is_valid_insertion_index, opposite_side, start_position_for_color


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
        """Create a new game lobby and register the creating player as leader.

        :param board_size: Side length of the square board.
        :param leader_display_name: Display name for the lobby leader.
        :param connection_id: WebSocket connection ID of the leader.
        :return: Connection state containing the new game and leader player.
        :raises ValueError: If the board size is invalid or the display name is taken/invalid.
        """
        if not is_valid_board_size(board_size):
            raise ValueError(f"Invalid board size: {board_size}")

        game = self.game_repo.create_game(board_size)
        leader = self._create_player_for_game(
            game=game,
            display_name=leader_display_name,
            connection_id=connection_id,
        )

        # Assign the newly created player as leader before persisting.
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
        """Join an existing lobby by join code.

        :param join_code: The lobby's join code (case-insensitive).
        :param display_name: Display name for the joining player.
        :param connection_id: WebSocket connection ID of the joining player.
        :return: Connection state containing the game and the new player.
        :raises ValueError: If the game is not found, not joinable, or the display name is taken/invalid.
        """
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
        """Look up a game by its ID.

        :param game_id: UUID of the game.
        :return: The game data, or ``None`` if not found.
        """
        return self.game_repo.find_by_game_id(game_id)

    def find_game_by_code(self, join_code: str) -> GameData | None:
        """Look up a game by its join code.

        :param join_code: The lobby's join code (case-insensitive).
        :return: The game data, or ``None`` if not found.
        """
        return self.game_repo.find_by_join_code(normalize_join_code(join_code))

    def get_game_state(self, game_id: UUID) -> GameState | None:
        """Fetch the full game state including players, tiles, and treasures.

        :param game_id: UUID of the game.
        :return: The full game state, or ``None`` if the game does not exist.
        """
        game = self.find_game(game_id)
        if game is None:
            return None

        players = self.player_repo.list_by_game_id(game.id)
        tiles = self.tile_repo.list_by_game_id(game.id)
        treasures_by_player = {player.id: self.treasure_repo.list_by_player_id(player.id) for player in players}
        return GameState.from_models(game, players, tiles, treasures_by_player)

    def get_connection_state(self, connection_id: str) -> ConnectionState | None:
        """Resolve an active WebSocket connection to its game and player.

        :param connection_id: WebSocket connection ID to look up.
        :return: Connection state for the associated game and player, or ``None`` if not found.
        """
        player = self.player_repo.find_by_connection_id(connection_id)
        if player is None:
            return None

        game = self.game_repo.find_by_game_id(player.game_id)
        if game is None:
            return None

        return ConnectionState(game=game, player=player)

    def leave_game(self, player_id: UUID) -> GameState | None:
        """Mark a player as departed and apply any resulting game state changes.

        :param player_id: UUID of the player leaving.
        :return: Updated game state, or ``None`` if the game was deleted (all players left).
        """
        player = self.player_repo.find_by_id(player_id)
        if player is None:
            return None

        game = self.game_repo.find_by_game_id(player.game_id)
        if game is None:
            return None

        players = self._mark_player_departed(player)

        return self._after_player_departure(game, player, players)

    def give_up(self, player_id: UUID) -> GameState | None:
        """Record a forfeit for a player and mark them as departed.

        :param player_id: UUID of the player forfeiting.
        :return: Updated game state, or ``None`` if the game was deleted.
        """
        player = self.player_repo.find_by_id(player_id)
        if player is None:
            return None

        game = self.game_repo.find_by_game_id(player.game_id)
        if game is None:
            return None

        # Only set FORFEITED if the player hasn't already received a result (e.g. WON).
        if player.result == PlayerResult.NONE:
            player.result = PlayerResult.FORFEITED
            self.player_repo.update_player(player)

        players = self._mark_player_departed(player)
        return self._after_player_departure(game, player, players)

    def start_game(self, player_id: UUID) -> GameState:
        """Start (or restart) the game; only the lobby leader may call this.

        Clears any previous runtime data, generates a new board, assigns treasures,
        and places all active players at their starting positions.

        :param player_id: UUID of the player requesting the start (must be the leader).
        :return: The initial game state for the new round.
        :raises ValueError: If the player/game is not found, the caller is not the leader,
            the game phase is wrong, or there are not enough players.
        """
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

        # Wipe leftover tiles and treasures from a previous round before generating new ones.
        self._clear_game_runtime(game.id, players)
        self._create_runtime_board(game)
        self._assign_treasures(active)

        # Place every player at their color-based starting corner; clear position for departed players.
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

        # Transition to GAME phase; the first active player (lowest join_order) goes first. TODO: randomize first player
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
        """Push the spare tile into the board and shift the row or column.
        If a player is currently on that row or column, they will be carried along with the shift,
        or pushed off and readded on the opposite side if they would fall off the board.

        :param player_id: UUID of the current player performing the shift.
        :param side: The side of the board to insert from.
        :param index: The row or column index to shift.
        :param rotation: Rotation to apply to the spare tile before insertion.
        :return: Updated game state after the shift.
        :raises ValueError: If it is not the player's turn, the insertion is blocked, or the index is invalid.
        """
        _, game = self._require_current_player(player_id, TurnPhase.SHIFT)
        if not is_valid_insertion_index(game.board_size, index):
            raise ValueError(f"Invalid insertion index: {index}")
        
        # Prevent re-inserting from the side that would immediately reverse the previous shift.
        # TODO: the client should disable that button
        if game.blocked_insertion_side == side and game.blocked_insertion_index == index:
            raise ValueError("That insertion is blocked")

        state = self.get_game_state(game.id)
        if state is None:
            raise ValueError("Game not found")
        state.board.shift_tile(side, index, rotation)
        for tile in state.tiles:
            self.tile_repo.update_tile(tile)

        # Carry any players that were sitting on the shifted row/column to their new position.
        for current in state.players:
            shifted = state.board.shift_player_position(
                self._player_position(current),
                side=side,
                index=index,
            )
            if shifted is None:
                continue
            current.position_x, current.position_y = shifted
            self.player_repo.update_player(current)

        # Transition to MOVE phase for the current player, blocking the reverse shift as the next valid action.
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
        """Move the current player to a reachable position and collect any treasure there.

        Ends the game if the player has won; otherwise advances to the next player's turn.

        :param player_id: UUID of the current player moving.
        :param x: Target column.
        :param y: Target row.
        :return: Updated game state after the move.
        :raises ValueError: If it is not the player's turn, the position is unreachable,
            or the player has no position.
        """
        player, game = self._require_current_player(player_id, TurnPhase.MOVE)
        state = self.get_game_state(game.id)
        if state is None:
            raise ValueError("Game not found")

        start = self._player_position(player)
        if start is None:
            raise ValueError("Player has no position")
        destination = (x, y)
        if not state.board.can_reach(start, destination):
            raise ValueError("Target position is not reachable")

        player.position_x = x
        player.position_y = y
        self.player_repo.update_player(player)
        self._collect_treasure_if_present(player, state.board.tile_treasure_at(destination))

        # Check win condition: all treasures collected and back at the home corner.
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
        """Skip the move phase and pass the turn to the next player.

        :param player_id: UUID of the current player ending their turn.
        :return: Updated game state with the next player's turn started.
        :raises ValueError: If it is not the player's turn or the game is not in the MOVE phase.
        """
        player, game = self._require_current_player(player_id, TurnPhase.MOVE)
        return self._finish_move(game, player)

    def _after_player_departure(
        self,
        game: GameData,
        player: PlayerData,
        players: list[PlayerData],
    ) -> GameState | None:
        """Handle turn/leader reassignment and end-game checks after a player departs."""
        remaining_players = active_players(players)

        # End the game if fewer than 2 players remain during an active game.
        if game.game_phase == GamePhase.GAME and len(remaining_players) < 2:
            if game.leader_player_id == player.id and remaining_players:
                next_leader = min(remaining_players, key=lambda current: current.join_order)
                game.leader_player_id = next_leader.id
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

        # Delete the game entirely when no players remain (e.g. lobby abandoned).
        if not remaining_players:
            self.game_repo.delete_game(game.id)
            return None

        # If the departing player held the turn, pass it to the next player in join-order.
        if game.current_player_id == player.id and game.game_phase == GamePhase.GAME:
            next_player = self._next_active_player(remaining_players, player.id)
            game.current_player_id = next_player.id
            game.turn_phase = TurnPhase.SHIFT
            game.blocked_insertion_side = None
            game.blocked_insertion_index = None

        # Hand the leader role to the earliest-joined remaining player.
        if game.leader_player_id == player.id:
            next_leader = min(remaining_players, key=lambda current: current.join_order)
            game.leader_player_id = next_leader.id
        game.revision += 1
        game = self.game_repo.update_game(game)
        state = self.get_game_state(game.id)
        return state

    def _mark_player_departed(self, player: PlayerData) -> list[PlayerData]:
        """Set player status to DEPARTED and return the updated player list for the game."""
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
        """Validate and create a new player for the given game."""
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
        """Advance to the next player's SHIFT phase."""
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
        """Fetch and validate that it is the player's turn in the expected phase."""
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
        """Delete all tiles and treasures for the game (used before starting a new round)."""
        for tile in self.tile_repo.list_by_game_id(game_id):
            self.tile_repo.delete_tile(tile.id)
        for player in players:
            for treasure in self.treasure_repo.list_by_player_id(player.id):
                self.treasure_repo.delete_treasure(treasure.id)

    def _create_runtime_board(self, game: GameData) -> None:
        """Generate and persist a fresh set of board tiles for the game."""
        board = Board.create_runtime(game)
        for tile in board.to_tile_data(game.id):
            self.tile_repo.create_tile(tile)

    def _assign_treasures(self, players: list[PlayerData]) -> None:
        """Distribute treasure assignments to all active players."""
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
        """Mark the player's active treasure as collected if it matches the tile's treasure."""
        if treasure_type is None:
            return
        target = self._active_treasure(player.id)
        if target is None or target.treasure_type != treasure_type:
            return
        target.collected = True
        target.collected_at = utcnow()
        self.treasure_repo.update_treasure(target)

    def _player_has_won(self, game: GameData, player: PlayerData) -> bool:
        """Return ``True`` if the player has collected all treasures and returned home."""
        if self._active_treasure(player.id) is not None:
            return False
        home_x, home_y = start_position_for_color(game.board_size, player.piece_color)
        return player.position_x == home_x and player.position_y == home_y

    def _active_treasure(self, player_id: UUID) -> TreasureData | None:
        """Return the player's next uncollected treasure, or ``None`` if all are collected."""
        treasures = sorted(self.treasure_repo.list_by_player_id(player_id), key=lambda current: current.order_index)
        for treasure in treasures:
            if not treasure.collected:
                return treasure
        return None

    def _next_active_player(self, players: list[PlayerData], current_player_id: UUID) -> PlayerData:
        """Return the next active player in join-order after the current one (wraps around)."""
        ordered = sorted(players, key=lambda current: current.join_order)
        current_index = next((index for index, player in enumerate(ordered) if player.id == current_player_id), -1)
        return ordered[(current_index + 1) % len(ordered)]

    def _player_position(self, player: PlayerData) -> tuple[int, int] | None:
        """Return the player's (x, y) position, or ``None`` if unset."""
        if player.position_x is None or player.position_y is None:
            return None
        return player.position_x, player.position_y
