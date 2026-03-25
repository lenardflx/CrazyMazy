from __future__ import annotations

from dataclasses import dataclass

from shared.lib.lobby import MIN_STARTABLE_PLAYERS, VALID_BOARD_SIZES
from shared.models import GamePhase, PlayerColor, TileType, TreasureType, TurnPhase
from shared.schema import GameSnapshotPayload, PublicPlayerPayload, TilePayload, ViewerPayload

PLAYER_COLOR_VALUES = {
    PlayerColor.RED: (210, 74, 74),
    PlayerColor.BLUE: (63, 109, 215),
    PlayerColor.GREEN: (80, 156, 93),
    PlayerColor.YELLOW: (209, 173, 59),
}


@dataclass(slots=True)
class TileView:
    tile_type: TileType
    rotation: int
    treasure_type: TreasureType | None = None
    is_fixed: bool = False
    home_color: PlayerColor | None = None


@dataclass(slots=True)
class ClientDisplayState:
    board_size: int = 7
    snapshot: GameSnapshotPayload | None = None
    board: list[list[TileView]] | None = None
    spare_tile: TileView | None = None

    @property
    def available_board_sizes(self) -> tuple[int, ...]:
        return tuple(sorted(VALID_BOARD_SIZES))

    def clear(self) -> None:
        self.snapshot = None
        self.board = None
        self.spare_tile = None

    @property
    def phase(self) -> GamePhase | None:
        return None if self.snapshot is None else GamePhase(self.snapshot["phase"])

    @property
    def is_lobby(self) -> bool:
        return self.phase == GamePhase.PREGAME

    @property
    def is_game(self) -> bool:
        return self.phase == GamePhase.GAME

    @property
    def is_post_game(self) -> bool:
        return self.phase == GamePhase.POSTGAME

    @property
    def code(self) -> str:
        return "" if self.snapshot is None else self.snapshot["code"]

    @property
    def players(self) -> list[PublicPlayerPayload]:
        if self.snapshot is None:
            return []
        return sorted(self.snapshot["players"], key=lambda current: current["join_order"])

    @property
    def viewer(self) -> ViewerPayload | None:
        return None if self.snapshot is None else self.snapshot["viewer"]

    @property
    def viewer_id(self) -> str:
        viewer = self.viewer
        return "" if viewer is None else viewer["player_id"]

    @property
    def leader_id(self) -> str:
        if self.snapshot is None:
            return ""
        return self.snapshot["leader_player_id"] or ""

    @property
    def current_player_id(self) -> str:
        if self.snapshot is None:
            return ""
        return self.snapshot["turn"]["current_player_id"] or ""

    @property
    def turn_phase(self) -> TurnPhase:
        if self.snapshot is None:
            return TurnPhase.SHIFT
        raw = self.snapshot["turn"]["turn_phase"]
        return TurnPhase.SHIFT if raw is None else TurnPhase(raw)

    @property
    def active_treasure_type(self) -> TreasureType | None:
        viewer = self.viewer
        if viewer is None:
            return None
        raw = viewer["active_treasure_type"]
        return None if raw is None else TreasureType(raw)

    def apply_snapshot(self, snapshot: GameSnapshotPayload) -> None:
        board, spare_tile = self._board_from_payload(snapshot["board_size"], snapshot["tiles"])
        self.snapshot = snapshot
        self.board_size = snapshot["board_size"]
        self.board = board
        self.spare_tile = spare_tile

    def can_viewer_start_lobby(self) -> bool:
        return self.is_lobby and self.viewer_id == self.leader_id and len(self.players) >= MIN_STARTABLE_PLAYERS

    def _apply_fixed_start_tiles(self, board: list[list[TileView]], size: int) -> None:
        # TODO: Move into snapshot and server
        corners = [
            ((0, 0), 1, PlayerColor.RED),
            ((size - 1, 0), 2, PlayerColor.BLUE),
            ((0, size - 1), 0, PlayerColor.GREEN),
            ((size - 1, size - 1), 3, PlayerColor.YELLOW),
        ]
        for (x, y), rotation, color in corners:
            board[y][x] = TileView(TileType.CORNER, rotation, None, True, color)

    def _board_from_payload(self, board_size: int, tiles: list[TilePayload]) -> tuple[list[list[TileView]], TileView]:
        board = [[TileView(TileType.STRAIGHT, 0) for _ in range(board_size)] for _ in range(board_size)]
        spare_tile: TileView | None = None
        for tile in tiles:
            tile_view = TileView(
                TileType(tile["tile_type"]),
                tile["rotation"],
                TreasureType(tile["treasure_type"]) if tile["treasure_type"] is not None else None,
            )
            if tile["is_spare"]:
                spare_tile = tile_view
                continue
            row = tile["row"]
            column = tile["column"]
            board[row][column] = tile_view
        self._apply_fixed_start_tiles(board, board_size)
        return board, spare_tile or TileView(TileType.CORNER, 0)
