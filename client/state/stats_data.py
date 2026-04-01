from __future__ import annotations

"""Local multiplayer stats derived from snapshot transitions and stored in app data."""

from dataclasses import dataclass
from typing import Any

from shared.game.snapshot import SnapshotGameState
from shared.types.enums import GamePhase, PlayerResult


@dataclass(slots=True)
class Stats:
    """Locally persisted player stats for completed multiplayer actions.

    These values are derived entirely on the client from incoming game snapshots.
    They are meant for lightweight personal progress, not authoritative ranking.
    """

    games_played: int = 0
    games_won: int = 0
    treasures_collected: int = 0
    moves_made: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Stats":
        """Build a stats object from persisted JSON data.

        Missing, malformed, or negative values fall back to ``0`` so old or
        partially edited ``app_data.json`` files still load safely.

        :param data: Raw JSON object from the ``stats`` section of app data.
        :return: A sanitized :class:`Stats` instance.
        """
        if not isinstance(data, dict):
            return cls()
        return cls(
            games_played=_int_value(data.get("games_played")),
            games_won=_int_value(data.get("games_won")),
            treasures_collected=_int_value(data.get("treasures_collected")),
            moves_made=_int_value(data.get("moves_made")),
        )

    def to_dict(self) -> dict[str, int]:
        """Serialize the stats to the ``stats`` JSON section stored by app data."""
        return {
            "games_played": self.games_played,
            "games_won": self.games_won,
            "treasures_collected": self.treasures_collected,
            "moves_made": self.moves_made,
        }

    @property
    def win_rate_percent(self) -> int:
        """Return the win rate as a rounded integer percentage."""
        if self.games_played <= 0:
            return 0
        return round((self.games_won / self.games_played) * 100)

    def record_snapshot_transition(
        self,
        previous: SnapshotGameState | None,
        current: SnapshotGameState,
    ) -> bool:
        """Update local stats from one snapshot transition.

        The method counts only viewer-visible multiplayer events:
        entering a live game, collecting treasures, completing a move, and
        winning when the match reaches postgame.

        :param previous: The previous snapshot seen by the client, or ``None`` on first sync.
        :param current: The newly received snapshot.
        :return: ``True`` when any stat changed and should be persisted.
        """
        changed = False

        if self._entered_live_game(previous, current):
            self.games_played += 1
            changed = True

        previous_viewer_treasures = 0
        if previous is not None and previous.game_id == current.game_id:
            previous_viewer = previous.viewer_player
            previous_viewer_treasures = 0 if previous_viewer is None else previous_viewer.collected_treasure_count

        viewer = current.viewer_player
        if viewer is not None:
            collected_delta = viewer.collected_treasure_count - previous_viewer_treasures
            if collected_delta > 0:
                self.treasures_collected += collected_delta
                changed = True

        if self._viewer_completed_move(previous, current):
            self.moves_made += 1
            changed = True

        if self._viewer_won(previous, current):
            self.games_won += 1
            changed = True

        return changed

    def _entered_live_game(
        self,
        previous: SnapshotGameState | None,
        current: SnapshotGameState,
    ) -> bool:
        """Return whether the viewer just entered an active multiplayer game."""
        if current.phase != GamePhase.GAME:
            return False
        if previous is None:
            return True
        if previous.game_id != current.game_id:
            return True
        return previous.phase != GamePhase.GAME

    def _viewer_completed_move(
        self,
        previous: SnapshotGameState | None,
        current: SnapshotGameState,
    ) -> bool:
        """Return whether the new snapshot contains a new viewer move event."""
        move = current.last_move
        if move is None or move.player_id != current.viewer_id:
            return False
        if previous is None or previous.game_id != current.game_id:
            return True
        return self._move_key(previous.last_move) != self._move_key(move)

    def _viewer_won(
        self,
        previous: SnapshotGameState | None,
        current: SnapshotGameState,
    ) -> bool:
        """Return whether the viewer newly reached postgame with a win result."""
        if current.phase != GamePhase.POSTGAME:
            return False
        viewer = current.viewer_player
        if viewer is None or viewer.result != PlayerResult.WON:
            return False
        if previous is None or previous.game_id != current.game_id:
            return True
        return previous.phase != GamePhase.POSTGAME

    @staticmethod
    def _move_key(move) -> tuple[str, tuple[tuple[int, int], ...], object] | None:
        """Create a stable identity for one move animation payload."""
        if move is None:
            return None
        return move.player_id, tuple(move.path), move.collected_treasure_type


def _int_value(value: Any) -> int:
    """Return a non-negative integer value, defaulting malformed input to ``0``."""
    return value if isinstance(value, int) and value >= 0 else 0
