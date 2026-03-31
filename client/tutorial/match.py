from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from client.state.runtime_state import BoardShiftAnimation, GameRuntimeState, PlayerMoveAnimation
from server.db.memory_repo import (
    GameRepositoryInMemory,
    PlayerRepositoryInMemory,
    TileRepositoryInMemory,
    TreasureRepositoryInMemory,
)
from server.service import GameService
from shared.game.board import Board
from shared.game.npc import NpcTurn
from shared.game.snapshot import SnapshotGameState
from shared.game.state import GameState
from shared.game.tile import Tile
from shared.lib.snapshot import make_game_snapshot_payload
from shared.protocol import ErrorCode
from shared.types.data import TreasureData
from shared.types.enums import InsertionSide, NpcDifficulty, TileOrientation, TileType, TreasureType, TurnPhase


@dataclass(slots=True, frozen=True)
class ScheduledNpcAction:
    """Represents one delayed NPC action queued during the tutorial turn."""

    kind: str
    delay: float
    turn: NpcTurn


class TutorialMatch:
    """Runs a complete local tutorial match on top of the real game service."""

    _NPC_SHIFT_DELAY_SECONDS = 0.45
    _NPC_MOVE_DELAY_SECONDS = 0.45
    _PLAYER_TUTORIAL_TREASURES = (
        TreasureType.CHEST,
        TreasureType.BOOK,
        TreasureType.GENIE,
        TreasureType.GOLDBAG,
        TreasureType.SKULL,
        TreasureType.GHOST,
    )
    _NPC_TUTORIAL_TREASURES = (
        TreasureType.RAT,
        TreasureType.DRAGON,
        TreasureType.CROWN,
        TreasureType.RING,
        TreasureType.OWL,
        TreasureType.FLY,
    )

    def __init__(self) -> None:
        self._service = GameService(
            GameRepositoryInMemory(),
            PlayerRepositoryInMemory(),
            TileRepositoryInMemory(),
            TreasureRepositoryInMemory(),
        )
        self.runtime = GameRuntimeState()
        self.snapshot: SnapshotGameState | None = None
        self._player_id: UUID | None = None
        self._npc_id: UUID | None = None
        self._scripted_phase_complete = False
        self._scripted_npc_turn_done = False
        self._pending_npc_actions: list[ScheduledNpcAction] = []
        self._npc_action_timer = 0.0
        self._bootstrap()

    @property
    def player_id(self) -> UUID:
        """Return the local tutorial player id."""
        if self._player_id is None:
            raise ValueError("Tutorial match has no player")
        return self._player_id

    @property
    def npc_id(self) -> UUID:
        """Return the tutorial NPC player id."""
        if self._npc_id is None:
            raise ValueError("Tutorial match has no NPC")
        return self._npc_id

    @property
    def scripted_npc_turn_done(self) -> bool:
        """Return whether the scripted NPC turn has finished and is ready to advance the tutorial."""
        return self._scripted_npc_turn_done

    @property
    def freeplay_started(self) -> bool:
        """Return whether the scripted tutorial phase has handed control to freeplay."""
        return self._scripted_phase_complete

    def start_freeplay(self) -> None:
        """Mark the guided phase as complete so the rest of the match runs as normal freeplay."""
        self._scripted_phase_complete = True

    def consume_scripted_npc_turn_done(self) -> None:
        """Clear the NPC-turn completion flag after the session advances past that step."""
        self._scripted_npc_turn_done = False

    def rotate_spare(self, direction: int) -> None:
        """Rotate the local spare tile preview by one step in the given direction."""
        self.runtime.spare_rotation = (self.runtime.spare_rotation + direction) % 4

    def shift_tile(self, side: InsertionSide, index: int) -> ErrorCode | None:
        """Attempt a tile shift. Returns None on success, ErrorCode on failure."""
        result = self._service.shift_tile(self.player_id, side, index, self.runtime.spare_rotation)
        if isinstance(result, ErrorCode):
            return result
        self.runtime.spare_rotation = 0
        self._apply_state(result)
        return None

    def move_player(self, x: int, y: int) -> ErrorCode | None:
        """Attempt a player move. Returns None on success, ErrorCode on failure."""
        result = self._service.move_player(self.player_id, x, y)
        if isinstance(result, ErrorCode):
            return result
        self._apply_state(result)
        return None

    def update(self, dt: float, *, npc_enabled: bool) -> None:
        """Advance animations and execute queued NPC actions when the tutorial allows it."""
        self._advance_animations(dt)

        if not npc_enabled or self.snapshot is None:
            return
        if self.runtime.shift_animation is not None or self.runtime.move_animation is not None:
            return

        if not self._pending_npc_actions and self._is_npc_turn():
            turn = self._next_npc_turn()
            self._pending_npc_actions = [
                ScheduledNpcAction("shift", self._NPC_SHIFT_DELAY_SECONDS, turn),
                ScheduledNpcAction(
                    "move" if turn.move_to is not None else "end_turn",
                    self._NPC_MOVE_DELAY_SECONDS,
                    turn,
                ),
            ]
            self._npc_action_timer = self._pending_npc_actions[0].delay

        if not self._pending_npc_actions:
            return

        self._npc_action_timer -= dt
        if self._npc_action_timer > 0:
            return

        action = self._pending_npc_actions.pop(0)
        self._execute_npc_action(action)
        if self._pending_npc_actions:
            self._npc_action_timer = self._pending_npc_actions[0].delay
        elif not self._scripted_phase_complete:
            self._scripted_npc_turn_done = True

    def _bootstrap(self) -> None:
        created = self._service.create_lobby(board_size=7, leader_display_name="You", connection_id="tutorial")
        if isinstance(created, ErrorCode):
            raise RuntimeError(f"Tutorial lobby creation failed: {created}")
        self._player_id = created.player.id

        added = self._service.add_npc(created.player.id, NpcDifficulty.EASY)
        if isinstance(added, ErrorCode):
            raise RuntimeError(f"Tutorial NPC creation failed: {added}")

        started = self._service.start_game(created.player.id)
        if isinstance(started, ErrorCode):
            raise RuntimeError(f"Tutorial game start failed: {started}")
        self._npc_id = next(
            player.id for player in started.players if player.id != created.player.id
        )
        configured = self._configure_opening_state(started.game.id)
        self._apply_state(configured)

    def _configure_opening_state(self, game_id: UUID) -> GameState:
        state = self._service.get_game_state(game_id)
        if state is None:
            raise ValueError("Tutorial game not found")

        board = self._build_tutorial_board(state.game.board_size)

        for tile in self._service.tile_repo.list_by_game_id(game_id):
            self._service.tile_repo.delete_tile(tile.id)
        for tile in board.to_tile_data(game_id):
            self._service.tile_repo.create_tile(tile)

        self._assign_tutorial_treasures()

        state.game.last_shift_side = None
        state.game.last_shift_index = None
        state.game.last_shift_rotation = None
        state.game.last_move_player_id = None
        state.game.last_move_path = None
        state.game.last_move_collected_treasure_type = None
        state.game.revision += 1
        self._service.game_repo.update_game(state.game)

        updated = self._service.get_game_state(game_id)
        if updated is None:
            raise ValueError("Tutorial game not found")
        return updated

    def _build_tutorial_board(self, board_size: int) -> Board:
        board = Board(board_size)
        board.tiles = {
            (0, 0): Tile(TileType.CORNER,    TileOrientation.EAST),
            (1, 0): Tile(TileType.STRAIGHT,  TileOrientation.NORTH),
            (2, 0): Tile(TileType.T,         TileOrientation.SOUTH,  TreasureType.CHEST),
            (3, 0): Tile(TileType.STRAIGHT,  TileOrientation.NORTH),
            (4, 0): Tile(TileType.T,         TileOrientation.SOUTH,  TreasureType.SWORD),
            (5, 0): Tile(TileType.T,         TileOrientation.EAST,   TreasureType.DRAGON),
            (6, 0): Tile(TileType.CORNER,    TileOrientation.SOUTH),
            (0, 1): Tile(TileType.CORNER,    TileOrientation.WEST,   TreasureType.LIZARD),
            (1, 1): Tile(TileType.STRAIGHT,  TileOrientation.EAST),
            (2, 1): Tile(TileType.STRAIGHT,  TileOrientation.EAST),
            (3, 1): Tile(TileType.CORNER,    TileOrientation.NORTH),
            (4, 1): Tile(TileType.CORNER,    TileOrientation.EAST),
            (5, 1): Tile(TileType.T,         TileOrientation.NORTH,  TreasureType.BAT),
            (6, 1): Tile(TileType.STRAIGHT,  TileOrientation.NORTH),
            (0, 2): Tile(TileType.T,         TileOrientation.EAST,   TreasureType.CROWN),
            (1, 2): Tile(TileType.STRAIGHT,  TileOrientation.EAST),
            (2, 2): Tile(TileType.T,         TileOrientation.NORTH,  TreasureType.BOOK),
            (3, 2): Tile(TileType.CORNER,    TileOrientation.SOUTH,  TreasureType.SPIDER),
            (4, 2): Tile(TileType.T,         TileOrientation.NORTH,  TreasureType.MAP),
            (5, 2): Tile(TileType.CORNER,    TileOrientation.EAST),
            (6, 2): Tile(TileType.T,         TileOrientation.WEST,   TreasureType.RING),
            (0, 3): Tile(TileType.STRAIGHT,  TileOrientation.EAST),
            (1, 3): Tile(TileType.T,         TileOrientation.NORTH,  TreasureType.GOBLIN),
            (2, 3): Tile(TileType.T,         TileOrientation.NORTH,  TreasureType.GENIE),
            (3, 3): Tile(TileType.CORNER,    TileOrientation.NORTH,  TreasureType.BUG),
            (4, 3): Tile(TileType.T,         TileOrientation.WEST,   TreasureType.PRINCESS),
            (5, 3): Tile(TileType.STRAIGHT,  TileOrientation.NORTH),
            (6, 3): Tile(TileType.STRAIGHT,  TileOrientation.NORTH),
            (0, 4): Tile(TileType.T,         TileOrientation.EAST,   TreasureType.ARMOR),
            (1, 4): Tile(TileType.STRAIGHT,  TileOrientation.NORTH),
            (2, 4): Tile(TileType.T,         TileOrientation.NORTH,  TreasureType.GOLDBAG),
            (3, 4): Tile(TileType.STRAIGHT,  TileOrientation.NORTH),
            (4, 4): Tile(TileType.T,         TileOrientation.EAST,   TreasureType.CANDLE),
            (5, 4): Tile(TileType.STRAIGHT,  TileOrientation.EAST),
            (6, 4): Tile(TileType.T,         TileOrientation.WEST,   TreasureType.KEYS),
            (0, 5): Tile(TileType.STRAIGHT,  TileOrientation.NORTH), 
            (1, 5): Tile(TileType.CORNER,    TileOrientation.SOUTH),
            (2, 5): Tile(TileType.CORNER,    TileOrientation.SOUTH,  TreasureType.FLY),
            (3, 5): Tile(TileType.STRAIGHT,  TileOrientation.NORTH),
            (4, 5): Tile(TileType.STRAIGHT,  TileOrientation.EAST),
            (5, 5): Tile(TileType.STRAIGHT,  TileOrientation.NORTH),
            (6, 5): Tile(TileType.CORNER,    TileOrientation.EAST,   TreasureType.OWL),
            (0, 6): Tile(TileType.CORNER,    TileOrientation.NORTH),
            (1, 6): Tile(TileType.STRAIGHT,  TileOrientation.NORTH,  TreasureType.RAT),
            (2, 6): Tile(TileType.T,         TileOrientation.NORTH,  TreasureType.EMERALD),
            (3, 6): Tile(TileType.CORNER,    TileOrientation.SOUTH),
            (4, 6): Tile(TileType.T,         TileOrientation.NORTH,  TreasureType.SKULL),
            (5, 6): Tile(TileType.T,         TileOrientation.SOUTH,  TreasureType.GHOST),
            (6, 6): Tile(TileType.CORNER,    TileOrientation.WEST),
        }
        board.spare = Tile(TileType.STRAIGHT, TileOrientation.NORTH)
        return board

    def _assign_tutorial_treasures(self) -> None:
        assignments = {
            self.player_id: self._PLAYER_TUTORIAL_TREASURES,
            self.npc_id: self._NPC_TUTORIAL_TREASURES,
        }
        for player_id, treasure_types in assignments.items():
            for treasure in self._service.treasure_repo.list_by_player_id(player_id):
                self._service.treasure_repo.delete_treasure(treasure.id)
            for order_index, treasure_type in enumerate(treasure_types):
                self._service.treasure_repo.create_treasure(
                    TreasureData(
                        player_id=player_id,
                        treasure_type=treasure_type,
                        order_index=order_index,
                    )
                )

    def _advance_animations(self, dt: float) -> None:
        shift_animation = self.runtime.shift_animation
        if shift_animation is not None:
            shift_animation.advance(dt)
            if shift_animation.is_finished:
                self.runtime.shift_animation = None

        move_animation = self.runtime.move_animation
        if move_animation is not None:
            move_animation.advance(dt)
            if move_animation.is_finished:
                self.runtime.move_animation = None

    def _is_npc_turn(self) -> bool:
        return (
            self.snapshot is not None
            and self.snapshot.phase.value == "GAME"
            and self.snapshot.turn.current_player_id is not None
            and self.snapshot.turn.current_player_id == str(self.npc_id)
        )

    def _next_npc_turn(self) -> NpcTurn:
        if not self._scripted_phase_complete:
            return NpcTurn(
                shift_side=InsertionSide.RIGHT,
                shift_index=5,
                shift_rotation=0,
                move_to=(6, 5),
            )

        state = self._service.get_game_state(self.snapshot_game_id)
        if state is None:
            raise ValueError("Tutorial game not found")
        if state.board is None:
            raise ValueError("Tutorial NPC turn requires a board")
        npc = state.npcs[self.npc_id]
        return npc.choose_turn(
            state.board,
            state.player_position(self.npc_id),
            state.target_position_for_player(self.npc_id),
            blocked_side=state.game.blocked_insertion_side,
            blocked_index=state.game.blocked_insertion_index,
            target_on_spare=state.target_on_spare_for_player(self.npc_id),
        )

    @property
    def snapshot_game_id(self) -> UUID:
        if self.snapshot is None:
            raise ValueError("Tutorial match has no snapshot")
        return UUID(self.snapshot.game_id)

    def _execute_npc_action(self, action: ScheduledNpcAction) -> None:
        state: GameState | ErrorCode
        if action.kind == "shift":
            state = self._service.shift_tile(
                self.npc_id,
                action.turn.shift_side,
                action.turn.shift_index,
                action.turn.shift_rotation,
            )
        elif action.kind == "move":
            move_to = action.turn.move_to
            if move_to is None:
                raise ValueError("NPC move action requires a target")
            state = self._service.move_player(self.npc_id, move_to[0], move_to[1])
        else:
            state = self._service.end_turn(self.npc_id)
        if not isinstance(state, ErrorCode):
            self._apply_state(state)

    def _apply_state(self, state: GameState) -> None:
        self.snapshot = SnapshotGameState.from_snapshot(
            make_game_snapshot_payload(
                state.game,
                state.players,
                state.tiles,
                state.treasures_by_player,
                viewer_player_id=str(self.player_id),
            )
        )

        shift = self.snapshot.last_shift
        self.runtime.shift_animation = (
            None
            if shift is None
            else BoardShiftAnimation(
                side=shift.side,
                index=shift.index,
            )
        )

        move = self.snapshot.last_move
        self.runtime.move_animation = (
            None
            if move is None or len(move.path) < 2
            else PlayerMoveAnimation(
                player_id=move.player_id,
                path=move.path,
                collected_treasure_type=move.collected_treasure_type,
            )
        )
