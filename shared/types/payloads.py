# Author: Lenard Felix

from __future__ import annotations

from typing import NotRequired, TypedDict

from shared.types.enums import (
    InsertionSide,
    NpcDifficulty,
    PlayerControllerKind,
)


class ErrorPayload(TypedDict):
    """Standard error payload returned by the server."""

    code: str
    message: str


class PositionPayload(TypedDict):
    """Serialized board coordinate."""

    x: int
    y: int


class TilePayload(TypedDict):
    """Serialized tile state used in snapshots and board-related events."""

    id: str
    tile_type: str
    rotation: int
    is_spare: bool
    treasure_type: str | None
    row: NotRequired[int]
    column: NotRequired[int]


class PublicPlayerPayload(TypedDict):
    """Player fields visible to every viewer of a game snapshot."""

    id: str
    display_name: str
    controller_kind: NotRequired[PlayerControllerKind]
    npc_difficulty: NotRequired[NpcDifficulty]
    status: str
    result: str
    placement: int | None
    join_order: int
    piece_color: str
    position: PositionPayload | None
    collected_treasures: list[str]
    remaining_treasure_count: int


class ViewerPayload(TypedDict):
    """Viewer-specific player metadata included only for the current recipient."""

    player_id: str
    is_leader: bool
    is_current_player: bool
    active_treasure_type: str | None
    collected_treasures: list[str]
    remaining_treasure_count: int


class TurnPayload(TypedDict):
    """Serialized turn-state metadata for the current game revision."""

    current_player_id: str | None
    turn_phase: str | None
    blocked_insertion_side: str | None
    blocked_insertion_index: int | None


class LastShiftPayload(TypedDict):
    """Animation metadata for the most recent tile shift."""

    side: str
    index: int
    rotation: int


class LastMovePayload(TypedDict):
    """Animation metadata for the most recent player movement."""

    player_id: str
    path: list[PositionPayload]
    collected_treasure_type: str | None


class GameSnapshotPayload(TypedDict):
    """Full client-facing snapshot of the game at a specific revision."""

    game_id: str
    code: str
    phase: str
    revision: int
    board_size: int
    leader_player_id: str | None
    turn: TurnPayload
    tiles: list[TilePayload]
    reachable_positions: list[PositionPayload]
    players: list[PublicPlayerPayload]
    viewer: ViewerPayload | None
    last_shift: NotRequired[LastShiftPayload]
    last_move: NotRequired[LastMovePayload]


class ClientCreateLobbyPayload(TypedDict):
    """Client request payload for creating a lobby."""

    board_size: int
    player_name: str


class ClientJoinGamePayload(TypedDict):
    """Client request payload for joining an existing game."""

    join_code: str
    player_name: str


class ClientGameShiftTilePayload(TypedDict):
    """Client request payload for a tile shift action."""

    insertion_side: str
    insertion_index: int
    rotation: int


class ClientGameMovePlayerPayload(TypedDict):
    """Client request payload for moving a player token."""

    x: int
    y: int


class ClientGameAddNpcPayload(TypedDict):
    """Client request payload for adding an NPC-controlled player to the lobby."""

    difficulty: NpcDifficulty


class ServerGameStartedPayload(TypedDict):
    """Server event payload announcing transition from lobby to active game."""

    game_id: str
    revision: int
    phase: str
    current_player_id: str | None
    turn_phase: str | None


class ServerGameTileShiftedPayload(TypedDict):
    """Server event payload for a completed tile shift."""

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
    """Server event payload for a completed player move."""

    game_id: str
    revision: int
    player_id: str
    position: PositionPayload
    active_treasure_type: str | None
    collected_treasure_type: str | None
    remaining_treasure_count: int


class ServerGameTurnChangedPayload(TypedDict):
    """Server event payload for turn ownership or phase changes."""

    game_id: str
    revision: int
    current_player_id: str | None
    turn_phase: str | None
    blocked_insertion_side: str | None
    blocked_insertion_index: int | None


class GamePlacementPayload(TypedDict):
    """Placement entry for a finished game result list."""

    player_id: str
    result: str
    placement: int | None


class ServerGameFinishedPayload(TypedDict):
    """Server event payload announcing final game results."""

    game_id: str
    revision: int
    winner_player_id: str | None
    placements: list[GamePlacementPayload]


class ServerGameLeftPayload(TypedDict):
    """Server payload describing why the client was removed from a game view."""

    reason: str
