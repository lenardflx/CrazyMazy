# Author: Tamay Engin, Lenard Felix, Raphael Eiden

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from shared.types.enums import (
    GameEndReason,
    GamePhase,
    InsertionSide,
    NpcDifficulty,
    PlayerControllerKind,
    PlayerColor,
    PlayerResult,
    PlayerSkin,
    PlayerStatus,
    TileType,
    TreasureType,
    TurnPhase,
)

# TODO: Lib
def utcnow() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


class PlayerData(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid4, primary_key=True)

    game_id: uuid.UUID = Field(foreign_key="game.id", index=True)

    # connection identifier
    connection_id: Optional[str] = Field(default=None, index=True, max_length=64)

    # Visible name shown in game
    display_name: str = Field(index=True, max_length=32)

    # Participation status in the current game lifecycle
    status: PlayerStatus = Field(default=PlayerStatus.ACTIVE, index=True)

    # Final outcome of this player within the current game loop
    result: PlayerResult = Field(default=PlayerResult.NONE)

    # Final ranking, if known
    placement: Optional[int] = Field(default=None, index=True)
   
    # Order Index in what the players joined, for leader transfer and turn order
    join_order: int = Field(index=True)

    # Player figure identity
    piece_color: PlayerColor = Field(index=True)
    skin: PlayerSkin = Field(default=PlayerSkin.DEFAULT)
    controller_kind: PlayerControllerKind = Field(default=PlayerControllerKind.HUMAN, index=True)
    npc_difficulty: Optional[NpcDifficulty] = Field(default=None)

    # Current game's position of the player
    position_x: Optional[int] = Field(default=None)
    position_y: Optional[int] = Field(default=None)

    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    finished_at: Optional[datetime] = Field(default=None)
    left_at: Optional[datetime] = Field(default=None)


class TileData(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    game_id: uuid.UUID = Field(default=None, foreign_key="game.id", index=True)

    # Position on the board
    row: Optional[int] = Field(default=None, index=True)
    column: Optional[int] = Field(default=None, index=True)

    # 0, 1, 2, 3 clockwise
    rotation: int = Field(default=0)

    # The one tile currently outside the board
    is_spare: bool = Field(default=False, index=True)

    # Treasure symbol printed on this tile, if any
    treasure_type: Optional[TreasureType] = Field(default=None)

    tile_type: TileType = Field(default=TileType.STRAIGHT)

    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class TreasureData(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # The player who needs collect this treasure
    player_id: uuid.UUID = Field(default=None, foreign_key="player.id", index=True)

    # The type of treasure
    treasure_type: TreasureType

    # Order of this target card in the players treasure sequence
    order_index: int = Field(index=True)

    # Whether this treasure has already been collected
    collected: bool = Field(default=False, index=True)

    # When this treasure was collected
    collected_at: Optional[datetime] = Field(default=None)


class GameData(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # code used for joining a game
    code: str = Field(index=True, unique=True, max_length=16)

    # Lobby's leader
    leader_player_id: Optional[UUID] = Field(default=None, foreign_key="player.id", index=True)

    # Board size. Must be odd, and enforced in service
    board_size: int = Field(default=7)

    # lifecycle of the game: lobby -> running match -> rematch screen
    game_phase: GamePhase = Field(default=GamePhase.PREGAME)

    # why the game ended once it reaches postgame
    end_reason: Optional[GameEndReason] = Field(default=None)

    # the maximum amount of seconds a player has time to insert a tile
    insert_timeout: int = Field(default=None)

    # the maximum amount of seconds a player has time to move
    move_timeout: int = Field(default=None)

    # Turn Phase during an active Match
    turn_phase: Optional[TurnPhase] = Field(default=None)

    # The timestamp at which the current move started
    turn_start_timestamp: Optional[int] = Field(default=None)

    # Current active player during the running match. Random pick at match start
    current_player_id: Optional[UUID] = Field(default=None, foreign_key="player.id", index=True)

    # version for snapshot syncing
    revision: int = Field(default=0)

    # Reverse insertion rule (no push back of last player's move)
    blocked_insertion_side: Optional[InsertionSide] = Field(default=None)
    blocked_insertion_index: Optional[int] = Field(default=None)

    # Last executed shift, used by clients for board-slide animation.
    last_shift_side: Optional[InsertionSide] = Field(default=None)
    last_shift_index: Optional[int] = Field(default=None)
    last_shift_rotation: Optional[int] = Field(default=None)

    # Last executed move, used by clients for walking and treasure animations.
    last_move_player_id: Optional[UUID] = Field(default=None, foreign_key="player.id", index=True)
    last_move_path: Optional[str] = Field(default=None)
    last_move_collected_treasure_type: Optional[TreasureType] = Field(default=None)

    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    started_at: Optional[datetime] = Field(default=None)
    ended_at: Optional[datetime] = Field(default=None)
