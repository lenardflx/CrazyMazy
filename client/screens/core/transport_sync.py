# Author: Lenard Felix

from __future__ import annotations

from client.network.errors import apply_server_error
from client.network.state import ClientState
from client.screens.core.scene_types import SceneTypes
from client.state.display_state import ClientDisplayState
from client.state.runtime_state import RuntimeState
from shared.protocol import ErrorCode


class TransportSync:
    """Watches the network transport for version changes and translates them into
    scene transitions and state updates.

    Call sync() once per frame. It returns the scene to navigate to when a
    transition is needed, or None when nothing changed.
    """

    def __init__(
        self,
        transport_state: ClientState,
        display_state: ClientDisplayState,
        runtime_state: RuntimeState,
    ) -> None:
        self._transport = transport_state
        self._display = display_state
        self._runtime = runtime_state
        self._seen_snapshot_version = 0
        self._seen_error_version = 0
        self._seen_game_left_version = 0

    def sync(self) -> tuple[SceneTypes | None, ErrorCode | None] | None:
        """Process pending transport events. Returns a scene to navigate to, or None."""
        target_scene: SceneTypes | None = None
        error: ErrorCode | None = None

        if self._transport.snapshot_version != self._seen_snapshot_version:
            self._seen_snapshot_version = self._transport.snapshot_version
            snapshot = self._transport.game_snapshot
            if snapshot is not None:
                self._display.apply_snapshot(snapshot)
                self._reset_runtime()
                target_scene = self._scene_from_snapshot()

        if self._transport.game_left_version != self._seen_game_left_version:
            self._seen_game_left_version = self._transport.game_left_version
            self._display.clear()
            self._reset_runtime()
            target_scene = SceneTypes.MAIN_MENU

        if self._transport.error_version != self._seen_error_version:
            self._seen_error_version = self._transport.error_version
            error = self._transport.last_error

        return target_scene, error

    def _reset_runtime(self) -> None:
        self._runtime.game.spare_rotation = 0
        self._runtime.clear_pending()
        self._runtime.clear_errors()

    def _scene_from_snapshot(self) -> SceneTypes:
        if self._display.is_post_game:
            return SceneTypes.POST_GAME
        if self._display.is_game:
            return SceneTypes.GAME
        return SceneTypes.LOBBY
