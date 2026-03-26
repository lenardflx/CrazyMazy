# Author: Raphael Eiden
 
from __future__ import annotations

from typing import Optional

from sqlmodel import Relationship

from shared.models import PlayerData, TileData, TreasureData, GameData


class PlayerTable(PlayerData, table=True):
    game: Optional["GameTable"] = Relationship(back_populates="players")
    treasure_cards: list["TreasureTable"] = Relationship(back_populates="player")


class TileTable(TileData, table=True):
    game: Optional["GameTable"] = Relationship(back_populates="tiles")


class TreasureTable(TreasureData, table=True):
    player: Optional["PlayerTable"] = Relationship(back_populates="treasure_cards")

class GameTable(GameData, table=True):
    players: list["PlayerTable"] = Relationship(back_populates="game")
    tiles: list["TileTable"] = Relationship(back_populates="game")
