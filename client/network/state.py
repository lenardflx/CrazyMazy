# Author: Lenard Felix

from __future__ import annotations

from dataclasses import dataclass

from shared.schema import ErrorPayload, GameSnapshotPayload


@dataclass
class ClientState:
    """Mutable client-side state projected from server responses."""

    last_error: ErrorPayload | None = None
    game_snapshot: GameSnapshotPayload | None = None
