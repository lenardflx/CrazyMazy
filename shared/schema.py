# Author: Lenard Felix

from __future__ import annotations

from typing import NotRequired, TypedDict

from shared.protocol import ErrorCode


class ErrorPayload(TypedDict):
    code: ErrorCode


class PositionPayload(TypedDict):
    x: int
    y: int


class TilePayload(TypedDict):
    id: str
    tile_type: str
    rotation: int
    is_spare: bool
    treasure_type: str | None
    row: NotRequired[int]
    column: NotRequired[int]


class PublicPlayerPayload(TypedDict):
    id: str
    display_name: str
    status: str
    result: str
    placement: int | None
    join_order: int
    piece_color: str
    position: PositionPayload | None
    collected_treasures: list[str]
    remaining_treasure_count: int


class ViewerPayload(TypedDict):
    player_id: str
    is_leader: bool
    is_current_player: bool
    active_treasure_type: str | None
    collected_treasures: list[str]
    remaining_treasure_count: int


class TurnPayload(TypedDict):
    current_player_id: str | None
    turn_phase: str | None
    blocked_insertion_side: str | None
    blocked_insertion_index: int | None


class GameSnapshotPayload(TypedDict):
    game_id: str
    code: str
    phase: str
    revision: int
    board_size: int
    leader_player_id: str | None
    turn: TurnPayload
    tiles: list[TilePayload]
    players: list[PublicPlayerPayload]
    viewer: ViewerPayload | None


class ClientCreateLobbyPayload(TypedDict):
    board_size: int
    player_name: str


class ClientJoinGamePayload(TypedDict):
    join_code: str
    player_name: str


class ClientGameShiftTilePayload(TypedDict):
    insertion_side: str
    insertion_index: int
    rotation: int


class ClientGameMovePlayerPayload(TypedDict):
    x: int
    y: int


class ServerGameStartedPayload(TypedDict):
    game_id: str
    revision: int
    phase: str
    current_player_id: str | None
    turn_phase: str | None


class ServerGameTileShiftedPayload(TypedDict):
    game_id: str
    revision: int
    insertion_side: str
    insertion_index: int
    tile: TilePayload
    current_player_id: str | None
    turn_phase: str | None
    blocked_insertion_side: str | None
    blocked_insertion_index: int | None


class ServerGamePlayerMovedPayload(TypedDict):
    game_id: str
    revision: int
    player_id: str
    position: PositionPayload
    active_treasure_type: str | None
    collected_treasure_type: str | None
    remaining_treasure_count: int


class ServerGameTurnChangedPayload(TypedDict):
    game_id: str
    revision: int
    current_player_id: str | None
    turn_phase: str | None
    blocked_insertion_side: str | None
    blocked_insertion_index: int | None


class GamePlacementPayload(TypedDict):
    player_id: str
    result: str
    placement: int | None


class ServerGameFinishedPayload(TypedDict):
    game_id: str
    revision: int
    winner_player_id: str | None
    placements: list[GamePlacementPayload]


class ServerGameLeftPayload(TypedDict):
    reason: str
