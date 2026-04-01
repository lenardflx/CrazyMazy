# Author: Lenard Felix

from __future__ import annotations

from client.network.state import ClientState
from client.screens.core.scene_types import SceneTypes
from shared.protocol import ErrorCode
from client.state.runtime_state import BoardShiftAnimation, PlayerMoveAnimation, RuntimeState
from client.state.app_data import ClientData
from shared.types.enums import GamePhase
from shared.game.snapshot import SnapshotGameState


class TransportSync:
    """
    Watches the network transport for version changes and translates them into
    scene transitions and state updates.

    Call sync() once per frame. It returns the scene to navigate to when a
    transition is needed, or None when nothing changed.
    """

    def __init__(
        self,
        transport_state: ClientState,
        runtime_state: RuntimeState,
        client_data: ClientData,
    ) -> None:
        self._transport = transport_state
        self._runtime = runtime_state
        self._client_data = client_data
        self._game_state: SnapshotGameState | None = None
        self._seen_snapshot_version = 0
        self._seen_error_version = 0
        self._seen_game_left_version = 0

    @property
    def game_state(self) -> SnapshotGameState | None:
        """
        Safety layer to only allow selection, no writes of the variable.
        """
        return self._game_state

    def sync(self) -> tuple[SceneTypes | None, ErrorCode | None] | None:
        """Process pending transport events. Returns a scene to navigate to, or None."""
        target_scene: SceneTypes | None = None
        error: ErrorCode | None = None

        # Check if a incoming snapshot has a new version. If so, update the game state and trigger the corresponding animations and scene transition.
        if self._transport.snapshot_version != self._seen_snapshot_version:
            self._seen_snapshot_version = self._transport.snapshot_version
            snapshot = self._transport.game_snapshot
            if snapshot is not None:
                previous_state = self._game_state
                self._game_state = SnapshotGameState.from_snapshot(snapshot)
                if self._client_data.stats.record_snapshot_transition(previous_state, self._game_state):
                    self._client_data.write_JSON()
                self._reset_runtime()
                self._start_animations(self._game_state)
                target_scene = self._scene_from_snapshot()

        if self._transport.game_left_version != self._seen_game_left_version:
            self._seen_game_left_version = self._transport.game_left_version
            self._game_state = None
            self._reset_runtime()
            self._runtime.game.shift_animation = None
            self._runtime.game.move_animation = None
            target_scene = SceneTypes.MAIN_MENU

        if self._transport.error_version != self._seen_error_version:
            self._seen_error_version = self._transport.error_version
            error = self._transport.last_error

        return target_scene, error

    def _reset_runtime(self) -> None:
        self._runtime.game.spare_rotation = 0

    def _start_animations(self, game_state: SnapshotGameState) -> None:
        """
        Check the game state for changes that require starting animations, and if so, start them.
        """

        # Shift animation. It moves a row in the board.
        shift = game_state.last_shift
        self._runtime.game.shift_animation = (
            None
            if shift is None
            else BoardShiftAnimation(
                side=shift.side,
                index=shift.index,
            )
        )

        # Move animation. It moves a player on the board and optionally shows a collected treasure
        move = game_state.last_move
        self._runtime.game.move_animation = (
            None
            if move is None or (len(move.path) < 2 and move.collected_treasure_type is None)
            else PlayerMoveAnimation(
                player_id=move.player_id,
                path=move.path,
                collected_treasure_type=move.collected_treasure_type,
            )
        )

    def _scene_from_snapshot(self) -> SceneTypes:
        """Determine the scene to transition to based on the current game state."""
        if self._game_state is None:
            return SceneTypes.MAIN_MENU
        if self._game_state.phase == GamePhase.POSTGAME:
            return SceneTypes.POST_GAME
        if self._game_state.phase == GamePhase.GAME:
            return SceneTypes.GAME
        return SceneTypes.LOBBY
