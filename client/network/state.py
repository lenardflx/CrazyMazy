# Author: Lenard Felix

from __future__ import annotations

from dataclasses import dataclass

from shared.types.payloads import ErrorPayload, GameSnapshotPayload, ServerGameLeftPayload
from shared.protocol import ErrorCode

@dataclass(slots=True)
class ClientState:
    """
    The current state of a client instance based on the packets received from the server.
    This class is mutable and treated as a singleton object, so there will only be one
    `ClientState` for the entire client runtime.

    When handling server events, the context is a `ClientState` object.
    Any updates and errors received by the server via such events can be
    directly written into the client state, by simply writing something like:
    ```
    @handler(ServerGameSnapshotEvent)
    def handle_server_snapshot(state: ClientState, event: ServerSnapshotEvent):
        state.game_snapshot = event.snapshot
    ```

    So, you can update the object provided by the `state` parameter to update
    the global ClientState.

    The `SceneManager` uses the `ClientState` to keep track of the currently displayed
    version/snapshot of the game to check whether the screen should be updated
    when a new event is received.
    """

    last_error: ErrorCode | None = None
    """
    We only process one error at once. 
    """

    game_snapshot: GameSnapshotPayload | None = None
    """
    """

    game_left: ServerGameLeftPayload | None = None

    error_version: int = 0
    snapshot_version: int = 0
    game_left_version: int = 0
