from __future__ import annotations

from dataclasses import dataclass

from shared.game.board import Board, Position
from shared.game.helper import home_color_for_position
from shared.game.tile import Tile
from shared.types.enums import (
    GamePhase,
    InsertionSide,
    NpcDifficulty,
    PlayerControllerKind,
    PlayerColor,
    PlayerResult,
    PlayerStatus,
    TreasureType,
    TurnPhase,
)
from shared.types.payloads import (
    GameSnapshotPayload,
    LastShiftPayload,
    PublicPlayerPayload,
    TilePayload,
    ViewerPayload,
)


@dataclass(slots=True)
class SnapshotPlayerState:
    id: str
    display_name: str
    join_order: int
    piece_color: PlayerColor
    position: Position | None
    status: PlayerStatus
    result: PlayerResult
    placement: int | None
    collected_treasures: list[TreasureType]
    remaining_treasure_count: int
    controller: PlayerControllerKind = PlayerControllerKind.HUMAN
    npc_difficulty: NpcDifficulty | None = None

    @classmethod
    def from_payload(cls, payload: PublicPlayerPayload) -> "SnapshotPlayerState":
        position_payload = payload["position"]
        position = None if position_payload is None else (position_payload["x"], position_payload["y"])
        return cls(
            id=payload["id"],
            display_name=payload["display_name"],
            join_order=payload["join_order"],
            controller=PlayerControllerKind(payload.get("controller_kind", PlayerControllerKind.HUMAN)),
            npc_difficulty=(
                None if payload.get("npc_difficulty") is None else NpcDifficulty(payload["npc_difficulty"])
            ),
            piece_color=PlayerColor(payload["piece_color"]),
            position=position,
            status=PlayerStatus(payload["status"]),
            result=PlayerResult(payload["result"]),
            placement=payload["placement"],
            collected_treasures=[TreasureType(treasure) for treasure in payload["collected_treasures"]],
            remaining_treasure_count=payload["remaining_treasure_count"],
        )

    @property
    def collected_treasure_count(self) -> int:
        return len(self.collected_treasures)

    @property
    def is_departed(self) -> bool:
        return self.status == PlayerStatus.DEPARTED

    @property
    def is_observer(self) -> bool:
        return self.status == PlayerStatus.OBSERVER

    @property
    def is_inactive(self) -> bool:
        return self.is_departed or self.is_observer

    # TODO: better layout, and this sucks :(
    def sidebar_status(self, *, post_game: bool = False) -> str | None:
        if self.is_departed:
            return "Left"
        if self.is_observer:
            return "Spectator"
        if post_game and self.placement is not None:
            return "Finished"
        return None


@dataclass(slots=True)
class SnapshotViewerState:
    player_id: str
    active_treasure_type: TreasureType | None

    @classmethod
    def from_payload(cls, payload: ViewerPayload) -> "SnapshotViewerState":
        active_treasure_type = payload["active_treasure_type"]
        return cls(
            player_id=payload["player_id"],
            active_treasure_type=None if active_treasure_type is None else TreasureType(active_treasure_type),
        )


@dataclass(slots=True)
class SnapshotTurnState:
    current_player_id: str | None
    turn_end_timestamp: int
    phase: TurnPhase | None
    blocked_insertion_side: InsertionSide | None = None
    blocked_insertion_index: int | None = None


@dataclass(slots=True, frozen=True)
class SnapshotLastShift:
    side: InsertionSide
    index: int
    rotation: int

    @classmethod
    def from_payload(cls, payload: LastShiftPayload) -> "SnapshotLastShift":
        return cls(
            side=InsertionSide(payload["side"]),
            index=payload["index"],
            rotation=payload["rotation"],
        )


@dataclass(slots=True, frozen=True)
class SnapshotLastMove:
    player_id: str
    path: list[Position]
    collected_treasure_type: TreasureType | None


@dataclass(slots=True)
class SnapshotGameState:
    game_id: str
    code: str
    phase: GamePhase
    revision: int
    board_size: int
    is_public: bool
    player_limit: int
    leader_player_id: str | None
    turn: SnapshotTurnState
    board: Board | None
    players: list[SnapshotPlayerState]
    reachable_positions: set[Position]
    viewer: SnapshotViewerState | None = None
    last_shift: SnapshotLastShift | None = None
    last_move: SnapshotLastMove | None = None

    @property
    def ordered_players(self) -> list[SnapshotPlayerState]:
        return sorted(self.players, key=lambda player: player.join_order)

    @property
    def viewer_id(self) -> str:
        return "" if self.viewer is None else self.viewer.player_id

    @property
    def viewer_player(self) -> SnapshotPlayerState | None:
        return next((player for player in self.players if player.id == self.viewer_id), None)

    @property
    def viewer_is_leader(self) -> bool:
        return self.viewer_id == (self.leader_player_id or "")

    @property
    def current_player_id(self) -> str:
        return "" if self.turn.current_player_id is None else self.turn.current_player_id

    @property
    def active_treasure_type(self) -> TreasureType | None:
        return None if self.viewer is None else self.viewer.active_treasure_type

    @property
    def viewer_turn(self) -> bool:
        return self.viewer_id == self.current_player_id

    @property
    def viewer_is_spectator(self) -> bool:
        viewer = self.viewer_player
        return viewer is not None and viewer.is_observer

    @property
    def can_add_npc(self) -> bool:
        return self.phase == GamePhase.PREGAME and self.viewer_is_leader and self.active_player_count < self.player_limit

    @property
    def can_start(self) -> bool:
        return self.phase == GamePhase.PREGAME and self.viewer_is_leader and self.active_player_count >= 2

    @property
    def active_player_count(self) -> int:
        return sum(1 for player in self.players if not player.is_inactive)

    @property
    def can_shift(self) -> bool:
        return self.viewer_turn and self.turn.phase == TurnPhase.SHIFT

    @property
    def can_move(self) -> bool:
        return self.viewer_turn and self.turn.phase == TurnPhase.MOVE

    def is_insertion_blocked(self, side: InsertionSide, index: int) -> bool:
        return self.turn.blocked_insertion_side == side and self.turn.blocked_insertion_index == index

    @property
    def turn_prompt(self) -> str:
        if self.viewer_is_spectator:
            return "Spectating"
        if self.can_shift:
            return "Your turn: insert a tile"
        if self.can_move:
            return "Your turn: move"
        return "Waiting for another player"

    @property
    def spare_tile(self) -> Tile | None:
        if self.board is None:
            return None
        return self.board.spare

    def rotated_spare_tile(self, rotation: int) -> Tile | None:
        tile = self.spare_tile
        if tile is None:
            return None
        return type(tile)(tile.type, (tile.orientation.value + rotation) % 4, tile.treasure)

    def tile_at(self, position: Position) -> Tile | None:
        if self.board is None:
            return None
        return self.board.tiles.get(position)

    def is_position_reachable(self, position: Position) -> bool:
        return position in self.reachable_positions

    def home_color_at(self, position: Position) -> PlayerColor | None:
        return home_color_for_position(self.board_size, position)

    @classmethod
    def from_snapshot(cls, snapshot: GameSnapshotPayload) -> "SnapshotGameState":
        turn_phase = snapshot["turn"]["turn_phase"]
        phase = GamePhase(snapshot["phase"])
        return cls(
            game_id=snapshot["game_id"],
            code=snapshot["code"],
            phase=phase,
            revision=snapshot["revision"],
            board_size=snapshot["board_size"],
            is_public=snapshot["is_public"],
            player_limit=snapshot["player_limit"],
            leader_player_id=snapshot["leader_player_id"],
            turn=SnapshotTurnState(
                current_player_id=snapshot["turn"]["current_player_id"],
                turn_end_timestamp=snapshot["turn"]["turn_end_timestamp"],
                phase=None if turn_phase is None else TurnPhase(turn_phase),
                blocked_insertion_side=(
                    None
                    if snapshot["turn"]["blocked_insertion_side"] is None
                    else InsertionSide(snapshot["turn"]["blocked_insertion_side"])
                ),
                blocked_insertion_index=snapshot["turn"]["blocked_insertion_index"],
            ),
            board=_board_from_snapshot(snapshot["board_size"], snapshot["tiles"], phase),
            players=[SnapshotPlayerState.from_payload(player) for player in snapshot["players"]],
            reachable_positions={(position["x"], position["y"]) for position in snapshot["reachable_positions"]},
            viewer=None if snapshot["viewer"] is None else SnapshotViewerState.from_payload(snapshot["viewer"]),
            last_shift=None if "last_shift" not in snapshot else SnapshotLastShift.from_payload(snapshot["last_shift"]),
            last_move=(
                None
                if "last_move" not in snapshot
                else SnapshotLastMove(
                    player_id=snapshot["last_move"]["player_id"],
                    path=[(position["x"], position["y"]) for position in snapshot["last_move"]["path"]],
                    collected_treasure_type=(
                        None
                        if snapshot["last_move"]["collected_treasure_type"] is None
                        else TreasureType(snapshot["last_move"]["collected_treasure_type"])
                    ),
                )
            ),
        )


def _board_from_snapshot(board_size: int, tiles: list[TilePayload], phase: GamePhase) -> Board | None:
    if not tiles:
        if phase == GamePhase.GAME:
            raise ValueError("Active game snapshot is missing board tiles")
        return None
    return Board.from_payloads(board_size, tiles)
