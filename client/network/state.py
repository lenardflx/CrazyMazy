# Author: Lenard Felix

from __future__ import annotations

from dataclasses import dataclass

from shared.types.payloads import ErrorPayload, GameSnapshotPayload, ServerGameLeftPayload


@dataclass(slots=True)
class ClientState:
    """
    Mutable client-side state projected from server responses.
    This state is used as state context for the client to compare
    incoming errors and snapshots with the current state of the client connection.
    """

    last_error: ErrorPayload | None = None
    game_snapshot: GameSnapshotPayload | None = None
    game_left: ServerGameLeftPayload | None = None
    error_version: int = 0
    snapshot_version: int = 0
    game_left_version: int = 0
