# Author: Lenard Felix

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class GamePhase(StrEnum):
    PREGAME = "PREGAME"
    GAME = "GAME"
    POSTGAME = "POSTGAME"


class TurnPhase(StrEnum):
    SHIFT = "SHIFT" # move tile
    MOVE = "MOVE" # move player position


class PlayerStatus(StrEnum):
    ACTIVE = "ACTIVE"
    OBSERVER = "OBSERVER"
    LEFT = "LEFT"


class PlayerResult(StrEnum):
    NONE = "NONE"
    WON = "WON"
    GAVE_UP = "GAVE_UP"


class PlayerColor(StrEnum):
    RED = "RED"
    BLUE = "BLUE"
    GREEN = "GREEN"
    YELLOW = "YELLOW"


class TileType(StrEnum):
    STRAIGHT = "STRAIGHT"
    CORNER = "CORNER"
    T = "T"


class TreasureType(StrEnum):
    BOOK = "BOOK"
    OWL = "OWL"
    # TODO: add other Treasures


class InsertionSide(StrEnum):
    TOP = "TOP"
    RIGHT = "RIGHT"
    BOTTOM = "BOTTOM"
    LEFT = "LEFT"


class Game(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # code used for joining a game
    code: str = Field(index=True, unique=True, max_length=16)

    # lifecycle of the game: lobby -> running match -> rematch screen
    phase: GamePhase = Field(default=GamePhase.PREGAME)

    # version for snapshot syncing
    revision: int = Field(default=0)

    # Board size. Must be odd, and enforced in service
    board_size: int = Field(default=7)

    # Lobby's leader
    leader_player_id: Optional[UUID] = Field(default=None, index=True)

    # Current active player during the running match. Random pick at match start
    current_player_id: Optional[UUID] = Field(default=None, index=True)

    # Turn Phase during an active Match
    turn_phase: Optional[TurnPhase] = Field(default=None)

    # Reverse insertion rule (no push back of last player's move)
    blocked_insertion_side: Optional[InsertionSide] = Field(default=None)
    blocked_insertion_index: Optional[int] = Field(default=None)

    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    started_at: Optional[datetime] = Field(default=None)
    ended_at: Optional[datetime] = Field(default=None)

    players: list["Player"] = Relationship(back_populates="game")
    tiles: list["Tile"] = Relationship(back_populates="game")


class Player(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    game_id: UUID = Field(foreign_key="game.id", index=True)

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

    # Current game's position of the player
    position_x: Optional[int] = Field(default=None)
    position_y: Optional[int] = Field(default=None)

    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    finished_at: Optional[datetime] = Field(default=None)
    left_at: Optional[datetime] = Field(default=None)

    game: Optional[Game] = Relationship(back_populates="players")
    treasure_cards: list["TreasureCard"] = Relationship(back_populates="player")


class Tile(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    game_id: UUID = Field(foreign_key="game.id", index=True)

    # Position on the board
    row: Optional[int] = Field(default=None, index=True)
    column: Optional[int] = Field(default=None, index=True)

    tile_type: TileType

    # 0, 1, 2, 3 clockwise
    rotation: int = Field(default=0)

    # The one tile currently outside the board
    is_spare: bool = Field(default=False, index=True)

    # Treasure symbol printed on this tile, if any
    treasure_type: Optional[TreasureType] = Field(default=None)

    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    game: Optional[Game] = Relationship(back_populates="tiles")


class TreasureCard(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    player_id: UUID = Field(foreign_key="player.id", index=True)

    # Order of this target card in the players treasure sequence
    order_index: int = Field(index=True)

    treasure_type: TreasureType

    # Whether this target has already been collected
    collected: bool = Field(default=False, index=True)
    collected_at: Optional[datetime] = Field(default=None)

    player: Optional[Player] = Relationship(back_populates="treasure_cards")
