# Author: Lenard Felix

from __future__ import annotations

from typing import NotRequired, TypedDict


class ErrorPayload(TypedDict):
    code: str
    message: str


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


class RoomSnapshotPayload(TypedDict):
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
