# Author: Lenard Felix
# TODO: Create Lib helper and add documentation. REVIEW afterwards, since logic critial

from __future__ import annotations

import time
from dataclasses import dataclass
from threading import Lock, Thread
from time import sleep
from uuid import UUID

from server.db.repo import GameRepository, PlayerRepository, TileRepository, TreasureRepository
from server.handlers._responses import snapshot_response
from server.network.outgoing import flush_outgoing
from shared.lib.lobby import MIN_STARTABLE_PLAYERS
from server.lib.game import can_join_game, is_valid_board_size, normalize_join_code
from server.lib.player import (
    active_players,
    is_display_name_taken,
    is_valid_display_name,
    next_available_color,
    next_join_order,
    normalize_display_name,
    session_players,
)
from shared.types.enums import (
    GameEndReason,
    GamePhase,
    InsertionSide,
    NpcDifficulty,
    PlayerResult,
    PlayerStatus,
    PlayerControllerKind,
    TreasureType,
    TurnPhase,
)

from shared.protocol import ErrorCode
from shared.types.data import GameData, PlayerData, TileData, TreasureData, utcnow
from shared.game.board import Board, is_valid_insertion_index, opposite_side
from shared.game.helper import assign_treasures, start_position_for_color
from shared.game.npc import Npc
from shared.game.state import GameState


@dataclass(slots=True)
class ConnectionState:
    game: GameData
    player: PlayerData


_NPC_ACTION_DELAY_SECONDS = 0.45


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
        self._running_npc_games: set[UUID] = set()
        self._running_npc_games_lock = Lock()

    def create_lobby(
        self,
        board_size: int,
        leader_display_name: str,
        connection_id: str,
    ) -> ConnectionState | ErrorCode:
        """Create a new game lobby and register the creating player as leader.

        :param board_size: Side length of the square board.
        :param leader_display_name: Display name for the lobby leader.
        :param connection_id: WebSocket connection ID of the leader.
        :return: Connection state containing the new game and leader player.
                    `INVALID_BOARD_SIZE` when the configured width of the board is out of range or even.
                    ``
        :raises ValueError: If the board size is invalid or the display name is taken/invalid.
        """
        if not is_valid_board_size(board_size):
            return ErrorCode.INVALID_BOARD_SIZE

        game = self.game_repo.create_game(board_size)
        leader = self._create_player_for_game(
            game=game,
            display_name=leader_display_name, # TODO: add constraints to display names (no symbols, length limit, etc.)
            connection_id=connection_id,
        )

        if isinstance(leader, ErrorCode):
            print("error with player")
            return leader

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
    ) -> ConnectionState | ErrorCode:
        """Join an existing lobby by join code.

        :param join_code: The lobby's join code (case-insensitive).
        :param display_name: Display name for the joining player.
        :param connection_id: WebSocket connection ID of the joining player.
        :return: Connection state containing the game and the new player.
                    `GAME_NOT_FOUND` error when the game does not exist.
                    `GAME_NOT_JOINABLE` when the game is not in lobby state.
        """
        game = self.find_game_by_code(join_code)
        if game is None:
            return ErrorCode.GAME_NOT_FOUND

        players = self.player_repo.list_by_game_id(game.id)
        if not can_join_game(game, players):
            return ErrorCode.GAME_NOT_JOINABLE

        player = self._create_player_for_game(
            game=game,
            display_name=display_name,
            connection_id=connection_id,
        )

        print("player: " + player)
        if isinstance(player, ErrorCode):
            print("error player")
            return player

        game.revision += 1
        self.game_repo.update_game(game)
        return ConnectionState(game=game, player=player)

    def add_npc(self, leader_player_id: UUID, difficulty: NpcDifficulty = NpcDifficulty.NORMAL) -> GameState | ErrorCode:
        leader = self.player_repo.find_by_id(leader_player_id)
        if leader is None:
            return ErrorCode.PLAYER_NOT_FOUND

        game = self.game_repo.find_by_game_id(leader.game_id)
        if game is None:
            return ErrorCode.GAME_NOT_FOUND
        if game.leader_player_id != leader.id:
            return ErrorCode.PLAYER_INSUFFICIENT_PERMISSION
        if game.game_phase != GamePhase.PREGAME:
            return ErrorCode.ADD_NPC_ONLY_IN_LOBBY

        players = self.player_repo.list_by_game_id(game.id)
        npc_name = Npc.generate_name({player.display_name for player in players})
        self._create_player_for_game(
            game=game,
            display_name=npc_name,
            connection_id=None,
            controller_kind=PlayerControllerKind.NPC,
            npc_difficulty=difficulty,
        )
        game.revision += 1
        game = self.game_repo.update_game(game)
        state = self.get_game_state(game.id)
        if state is None:
            return ErrorCode.GAME_NOT_FOUND
        return state

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

        return self._after_player_inactivation(game, player, players)

    def give_up(self, player_id: UUID) -> GameState | None:
        """Move a player from active participation into spectator mode.

        :param player_id: UUID of the player giving up.
        :return: Updated game state, or ``None`` if the game was deleted.
        """
        player = self.player_repo.find_by_id(player_id)
        if player is None:
            return None

        game = self.game_repo.find_by_game_id(player.game_id)
        if game is None:
            return None

        players = self._mark_player_observer(player)
        return self._after_player_inactivation(game, player, players)

    def start_game(self, player_id: UUID) -> GameState | ErrorCode:
        """Start (or restart) the game; only the lobby leader may call this.

        Clears any previous runtime data, generates a new board, assigns treasures,
        and places all active players at their starting positions.

        :param player_id: UUID of the player requesting the start (must be the leader).
        :return: The initial game state for the new round.
        """
        player = self.player_repo.find_by_id(player_id)
        if player is None:
            return ErrorCode.PLAYER_NOT_FOUND

        game = self.game_repo.find_by_game_id(player.game_id)
        if game is None:
            return ErrorCode.GAME_NOT_FOUND
        if game.leader_player_id != player.id:
            return ErrorCode.PLAYER_INSUFFICIENT_PERMISSION
        if game.game_phase not in (GamePhase.PREGAME, GamePhase.POSTGAME):
            return ErrorCode.GAME_NOT_STARTABLE

        players = self.player_repo.list_by_game_id(game.id)
        active = sorted(active_players(players), key=lambda current: current.join_order)
        if len(active) < MIN_STARTABLE_PLAYERS:
            return ErrorCode.PLAYER_COUNT_INSUFFICIENT

        # Wipe leftover tiles and treasures from a previous round before generating new ones.
        self._clear_game_runtime(game.id, players)
        self._create_runtime_board(game)
        self._assign_treasures(active)

        # Place every active player at their home corner; inactive players stay off-board.
        for current in players:
            if current.status != PlayerStatus.ACTIVE:
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
        game.turn_start_timestamp = time.time_ns() // 1_000_000
        game.current_player_id = active[0].id
        game.blocked_insertion_side = None
        game.blocked_insertion_index = None
        game.last_shift_side = None
        game.last_shift_index = None
        game.last_shift_rotation = None
        game.last_move_player_id = None
        game.last_move_path = None
        game.last_move_collected_treasure_type = None
        game.started_at = utcnow()
        game.ended_at = None
        game.revision += 1
        game = self.game_repo.update_game(game)
        state = self.get_game_state(game.id)
        if state is None:
            return ErrorCode.GAME_NOT_FOUND
        return state

    def shift_tile(self, player_id: UUID, side: InsertionSide, index: int, rotation: int) -> GameState | ErrorCode:
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
        _, game = self._require_current_player(player_id, TurnPhase.SHIFT) # todo: fix error handling here, currently unsafe as tuple unpacking does not always work!
        if not is_valid_insertion_index(game.board_size, index):
            raise ValueError(f"Invalid insertion index: {index}")

        # Prevent re-inserting from the side that would immediately reverse the previous shift.
        # TODO: the client should disable that button
        if game.blocked_insertion_side == side and game.blocked_insertion_index == index:
            return ErrorCode.TILE_INSERTION_BLOCKED

        state = self.get_game_state(game.id)
        if state is None:
            return ErrorCode.GAME_NOT_FOUND

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
        game.turn_start_timestamp = time.time_ns() // 1_000_000
        game.blocked_insertion_side = opposite_side(side)
        game.blocked_insertion_index = index
        game.last_shift_side = side
        game.last_shift_index = index
        game.last_shift_rotation = rotation
        game.last_move_player_id = None
        game.last_move_path = None
        game.last_move_collected_treasure_type = None
        game.revision += 1
        game = self.game_repo.update_game(game)
        updated = self.get_game_state(game.id)
        if updated is None:
            return ErrorCode.GAME_NOT_FOUND
        return updated

    def move_player(self, player_id: UUID, x: int, y: int) -> GameState | ErrorCode:
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
            return ErrorCode.GAME_NOT_FOUND

        start = self._player_position(player)
        if start is None:
            return ErrorCode.PLAYER_HAS_NO_POSITION
        destination = (x, y)
        path = state.board.path_to(start, destination)
        if path is None:
            return ErrorCode.TARGET_POSITION_UNREACHABLE

        player.position_x = x
        player.position_y = y
        self.player_repo.update_player(player)
        collected_treasure_type = self._collect_treasure_if_present(player, state.board.tile_treasure_at(destination))
        game.last_shift_side = None
        game.last_shift_index = None
        game.last_shift_rotation = None
        game.last_move_player_id = player.id
        game.last_move_path = _serialize_position_path(path)
        game.last_move_collected_treasure_type = collected_treasure_type

        # Check win condition: all treasures collected and back at the home corner.
        if self._player_has_won(game, player):
            player.result = PlayerResult.WON
            player.placement = 1
            player.finished_at = utcnow()
            self.player_repo.update_player(player)
            players = self.player_repo.list_by_game_id(game.id)
            self._finalize_postgame_players(players, winner_id=player.id)
            game.game_phase = GamePhase.POSTGAME
            game.end_reason = GameEndReason.COMPLETED
            game.current_player_id = None
            game.turn_phase = None
            game.ended_at = utcnow()
        game.revision += 1
        game = self.game_repo.update_game(game)
        updated = self.get_game_state(game.id)
        if updated is None:
            return ErrorCode.GAME_NOT_FOUND
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

    def _after_player_inactivation(
        self,
        game: GameData,
        player: PlayerData,
        players: list[PlayerData],
    ) -> GameState | None:
        """Handle turn/leader reassignment and end-game checks after a player stops being active."""
        remaining_players = active_players(players)
        remaining_session_players = session_players(players)

        # End the game if fewer than 2 players remain during an active game.
        if game.game_phase == GamePhase.GAME and len(remaining_players) < 2:
            if game.leader_player_id == player.id and remaining_session_players:
                next_leader = self._next_leader(remaining_players, remaining_session_players)
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
                self._finalize_postgame_players(players, winner_id=winner.id)
            else:
                self._finalize_postgame_players(players)
            game.revision += 1
            game = self.game_repo.update_game(game)
            state = self.get_game_state(game.id)
            return state

        # Delete the game entirely when no session participants remain.
        if not remaining_session_players:
            self.game_repo.delete_game(game.id)
            return None

        # If the inactive player held the turn, pass it to the next active player in join-order.
        if game.current_player_id == player.id and game.game_phase == GamePhase.GAME:
            next_player = self._next_active_player(remaining_players, player.id)
            game.current_player_id = next_player.id
            game.turn_phase = TurnPhase.SHIFT
            game.turn_start_timestamp = time.time_ns() // 1_000_000
            game.blocked_insertion_side = None
            game.blocked_insertion_index = None
            game.last_shift_side = None
            game.last_shift_index = None
            game.last_shift_rotation = None
            game.last_move_player_id = None
            game.last_move_path = None
            game.last_move_collected_treasure_type = None

        # Hand the leader role to an active player when possible, otherwise the earliest remaining session player.
        if game.leader_player_id == player.id:
            next_leader = self._next_leader(remaining_players, remaining_session_players)
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

    def _mark_player_observer(self, player: PlayerData) -> list[PlayerData]:
        """Set player status to OBSERVER and keep them connected to the session."""
        if player.status != PlayerStatus.OBSERVER:
            player.status = PlayerStatus.OBSERVER
            player.position_x = None
            player.position_y = None
            player.finished_at = utcnow()
            self.player_repo.update_player(player)

        return self.player_repo.list_by_game_id(player.game_id)

    def _create_player_for_game(
        self,
        game: GameData,
        display_name: str,
        connection_id: str | None,
        *,
        controller_kind: PlayerControllerKind = PlayerControllerKind.HUMAN,
        npc_difficulty: NpcDifficulty | None = None,
    ) -> PlayerData | ErrorCode:
        """Validate and create a new player for the given game."""
        players = self.player_repo.list_by_game_id(game.id)
        if not is_valid_display_name(display_name):
            return ErrorCode.DISPLAY_NAME_ILLEGAL
        if is_display_name_taken(players, display_name):
            return ErrorCode.DISPLAY_NAME_TAKEN

        join_order = next_join_order(players)
        piece_color = next_available_color(players)
        if piece_color is None:
            # Actually, the error is "no player color available"
            # but this can only happen when the game is full.
            return ErrorCode.GAME_FULL

        return self.player_repo.create_player(
            display_name=normalize_display_name(display_name),
            connection_id=connection_id,
            game_id=game.id,
            join_order=join_order,
            piece_color=piece_color,
            controller_kind=controller_kind,
            npc_difficulty=npc_difficulty,
        )

    def _finish_move(self, game: GameData, player: PlayerData) -> GameState | ErrorCode:
        """Advance to the next player's SHIFT phase."""
        next_player = self._next_active_player(active_players(self.player_repo.list_by_game_id(game.id)), player.id)
        game.current_player_id = next_player.id
        game.turn_phase = TurnPhase.SHIFT
        game.turn_start_timestamp = time.time_ns() // 1_000_000
        game.blocked_insertion_side = None
        game.blocked_insertion_index = None
        game.last_shift_side = None
        game.last_shift_index = None
        game.last_shift_rotation = None
        game.revision += 1
        game = self.game_repo.update_game(game)
        state = self.get_game_state(game.id)
        if state is None:
            return ErrorCode.GAME_NOT_FOUND
        return state

    def _require_current_player(self, player_id: UUID, phase: TurnPhase) -> tuple[PlayerData, GameData] | ErrorCode:
        """Fetch and validate that it is the player's turn in the expected phase."""
        player = self.player_repo.find_by_id(player_id)
        if player is None:
            return ErrorCode.PLAYER_NOT_FOUND
        game = self.game_repo.find_by_game_id(player.game_id)
        if game is None:
            return ErrorCode.GAME_NOT_FOUND
        if game.game_phase != GamePhase.GAME:
            return ErrorCode.GAME_INACTIVE
        if game.current_player_id != player.id:
            return ErrorCode.PLAYER_NO_TURN
        if game.turn_phase != phase:
            return ErrorCode.UNEXPECTED_TURN_PHASE
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

    def _collect_treasure_if_present(self, player: PlayerData, treasure_type: TreasureType | None) -> TreasureType | None:
        """Mark the player's active treasure as collected if it matches the tile's treasure."""
        if treasure_type is None:
            return None
        target = self._active_treasure(player.id)
        if target is None or target.treasure_type != treasure_type:
            return None
        target.collected = True
        target.collected_at = utcnow()
        self.treasure_repo.update_treasure(target)
        return treasure_type

    def _player_has_won(self, game: GameData, player: PlayerData) -> bool:
        """Return ``True`` if the player has collected all treasures and returned home."""
        if self._active_treasure(player.id) is not None:
            return False
        home_x, home_y = start_position_for_color(game.board_size, player.piece_color)
        return player.position_x == home_x and player.position_y == home_y

    def _finalize_postgame_players(self, players: list[PlayerData], winner_id: UUID | None = None) -> None:
        finished_at_fallback = utcnow()
        placement = 2 if winner_id is not None else 1

        ranked_players = sorted(
            (player for player in players if player.status != PlayerStatus.DEPARTED and player.id != winner_id),
            key=lambda player: (
                player.status == PlayerStatus.OBSERVER,
                player.finished_at or finished_at_fallback,
                player.join_order,
            ),
        )

        for player in ranked_players:
            player.placement = placement
            if player.status == PlayerStatus.OBSERVER:
                player.result = PlayerResult.FORFEITED
            if player.finished_at is None:
                player.finished_at = utcnow()
            self.player_repo.update_player(player)
            placement += 1

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
        current_index = next((index for index, player in enumerate(ordered) if player.id == current_player_id), None)
        if current_index is not None:
            return ordered[(current_index + 1) % len(ordered)]

        current_player = self.player_repo.find_by_id(current_player_id)
        if current_player is None:
            return ordered[0]

        for player in ordered:
            if player.join_order > current_player.join_order:
                return player
        return ordered[0]

    def _next_leader(self, active: list[PlayerData], session: list[PlayerData]) -> PlayerData:
        """Choose a replacement leader, preferring active players over spectators."""
        pool = active if active else session
        return min(pool, key=lambda current: current.join_order)

    def _player_position(self, player: PlayerData) -> tuple[int, int] | None:
        """Return the player's (x, y) position, or ``None`` if unset."""
        if player.position_x is None or player.position_y is None:
            return None
        return player.position_x, player.position_y

    def schedule_npc_turns(self, state: GameState) -> None:
        if not self._has_pending_npc_turn(state):
            return

        game_id = state.game.id
        with self._running_npc_games_lock:
            if game_id in self._running_npc_games:
                return
            self._running_npc_games.add(game_id)

        Thread(target=self._run_npc_turns, args=(game_id,), daemon=True).start()

    def _run_npc_turns(self, game_id: UUID) -> None:
        try:
            while True:
                sleep(_NPC_ACTION_DELAY_SECONDS)
                state = self.get_game_state(game_id)
                if state is None or not self._has_pending_npc_turn(state):
                    return

                updated = self._perform_next_npc_action(state)
                flush_outgoing(snapshot_response(updated))
        finally:
            with self._running_npc_games_lock:
                self._running_npc_games.discard(game_id)

    def _has_pending_npc_turn(self, state: GameState) -> bool:
        return (
            state.game.game_phase == GamePhase.GAME
            and state.game.current_player_id is not None
            and state.game.current_player_id in state.npcs
        )

    def _perform_next_npc_action(self, state: GameState) -> GameState:
        game = state.game
        npc = state.npcs[game.current_player_id]
        turn = npc.choose_turn(
            state,
            blocked_side=game.blocked_insertion_side,
            blocked_index=game.blocked_insertion_index,
        )
        updated = self.shift_tile(npc.player_id, turn.shift_side, turn.shift_index, turn.shift_rotation)
        flush_outgoing(snapshot_response(updated))
        sleep(_NPC_ACTION_DELAY_SECONDS)
        if turn.move_to is None:
            return self.end_turn(npc.player_id)
        return self.move_player(npc.player_id, turn.move_to[0], turn.move_to[1])

# TODO: is this clean? + probably should be in lib
def _serialize_position_path(path: list[tuple[int, int]]) -> str:
    return ";".join(f"{x},{y}" for x, y in path)
