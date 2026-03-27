from __future__ import annotations

from dataclasses import dataclass

from shared.schema import GameSnapshotPayload
from shared.state.game_state import GameState


@dataclass(slots=True)
class StateEngine:
    """Thin state holder built on top of the shared game_state domain."""

    current: GameState | None = None

    def clear(self) -> None:
        self.current = None

    def apply_snapshot(self, snapshot: GameSnapshotPayload) -> GameState:
        self.current = GameState.from_snapshot(snapshot)
        return self.current

    def require_state(self) -> GameState:
        if self.current is None:
            raise ValueError("No game state loaded")
        return self.current
